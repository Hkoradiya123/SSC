from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.config import settings
from app.database import get_db
from app.models import User, Payment, FinanceTransaction, AdminChatMessage
from app.schemas import AdminChatCreate, AdminChatResponse
from app.middleware.auth import get_admin_user, get_current_user
from app.utils.logger import log_action, log_error

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List)
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""

    users = db.query(User).offset(skip).limit(limit).all()
    log_action("Admin viewed all users", user_id=admin.id)
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_premium": user.is_premium,
            "runs": user.runs,
            "matches": user.matches,
            "wickets": user.wickets,
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.put("/users/{user_id}/premium")
async def toggle_user_premium(
    user_id: int,
    days: int = 30,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Toggle user premium status (admin only)"""

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_premium = not user.is_premium

    if user.is_premium:
        from datetime import datetime, timedelta
        user.premium_expiry = datetime.utcnow() + timedelta(days=days)
        user.premium_start_date = datetime.utcnow()
    else:
        user.premium_expiry = None

    db.commit()
    log_action("Admin toggled user premium", user_id=admin.id,
               details=f"User {user_id}")

    return {"message": f"User premium status updated"}


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate user (admin only)"""

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    db.commit()

    log_action("Admin deactivated user", user_id=admin.id,
               details=f"User {user_id}")

    return {"message": "User deactivated successfully"}


@router.get("/stats")
async def get_system_stats(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)"""

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    premium_users = db.query(User).filter(User.is_premium == True).count()
    total_matches = sum([u.matches for u in db.query(User).all()])

    paid_user_ids = {
        row[0]
        for row in db.query(Payment.user_id)
        .filter(Payment.status == "completed")
        .distinct()
        .all()
    }
    active_players = db.query(User).filter(User.is_active == True, User.role == "player").all()
    unpaid_players = [player for player in active_players if player.id not in paid_user_ids]

    pending_funds = len(unpaid_players) * settings.PREMIUM_COST

    total_collected = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(
        Payment.status == "completed"
    ).scalar() or 0.0
    manual_credits = db.query(func.coalesce(func.sum(FinanceTransaction.amount), 0.0)).filter(
        FinanceTransaction.transaction_type == "credit",
        FinanceTransaction.category == "manual_credit",
    ).scalar() or 0.0
    total_debits = db.query(func.coalesce(func.sum(FinanceTransaction.amount), 0.0)).filter(
        FinanceTransaction.transaction_type == "debit",
    ).scalar() or 0.0
    funds_remaining = round((total_collected + manual_credits) - total_debits, 2)

    unread_chat_messages = db.query(AdminChatMessage).filter(
        AdminChatMessage.sender_role == "player",
        AdminChatMessage.is_read == False,
    ).count()

    log_action("Admin viewed system stats", user_id=admin.id)

    return {
        "total_users": total_users,
        "active_users": active_users,
        "premium_users": premium_users,
        "total_matches": total_matches,
        "pending_funds": pending_funds,
        "funds_remaining": funds_remaining,
        "unread_chat_messages": unread_chat_messages,
    }


@router.get("/chats")
async def get_chat_threads(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get admin chat thread summary by player."""
    players = db.query(User).filter(User.role == "player", User.is_active == True).all()

    threads = []
    for player in players:
        messages = db.query(AdminChatMessage).filter(
            AdminChatMessage.user_id == player.id
        ).order_by(AdminChatMessage.created_at.desc()).limit(1).all()

        last_message = messages[0] if messages else None
        unread_count = db.query(AdminChatMessage).filter(
            AdminChatMessage.user_id == player.id,
            AdminChatMessage.sender_role == "player",
            AdminChatMessage.is_read == False,
        ).count()

        threads.append(
            {
                "user_id": player.id,
                "name": player.name,
                "email": player.email,
                "unread_count": unread_count,
                "last_message": last_message.message if last_message else None,
                "last_message_at": last_message.created_at if last_message else None,
            }
        )

    threads.sort(key=lambda item: item["last_message_at"] or datetime.min, reverse=True)
    return threads


@router.get("/chats/{user_id}", response_model=list[AdminChatResponse])
async def get_chat_thread(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get full chat thread for a player."""
    user = db.query(User).filter(User.id == user_id, User.role == "player").first()
    if not user:
        raise HTTPException(status_code=404, detail="Player not found")

    messages = db.query(AdminChatMessage).filter(
        AdminChatMessage.user_id == user_id
    ).order_by(AdminChatMessage.created_at.asc()).all()

    db.query(AdminChatMessage).filter(
        AdminChatMessage.user_id == user_id,
        AdminChatMessage.sender_role == "player",
        AdminChatMessage.is_read == False,
    ).update({"is_read": True})
    db.commit()

    return messages


@router.post("/chats/{user_id}", response_model=AdminChatResponse)
async def send_admin_chat_message(
    user_id: int,
    payload: AdminChatCreate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Send a message from admin to a player."""
    user = db.query(User).filter(User.id == user_id, User.role == "player").first()
    if not user:
        raise HTTPException(status_code=404, detail="Player not found")

    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    chat = AdminChatMessage(
        user_id=user_id,
        sender_role="admin",
        message=message,
        is_read=False,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    log_action("Admin chat message sent", user_id=admin.id, details=f"to={user_id}")
    return chat


@router.get("/my-chat", response_model=list[AdminChatResponse])
async def get_my_chat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current player's chat with admin."""
    messages = db.query(AdminChatMessage).filter(
        AdminChatMessage.user_id == current_user.id
    ).order_by(AdminChatMessage.created_at.asc()).all()

    db.query(AdminChatMessage).filter(
        AdminChatMessage.user_id == current_user.id,
        AdminChatMessage.sender_role == "admin",
        AdminChatMessage.is_read == False,
    ).update({"is_read": True})
    db.commit()

    return messages


@router.post("/my-chat", response_model=AdminChatResponse)
async def send_message_to_admin(
    payload: AdminChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send message to admin from current player."""
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    chat = AdminChatMessage(
        user_id=current_user.id,
        sender_role="player",
        message=message,
        is_read=False,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    log_action("Player chat message sent", user_id=current_user.id)
    return chat
