from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Notification, User
from app.middleware.auth import get_current_user
from app.schemas import NotificationResponse
from app.utils.logger import log_action
from app.utils.premium import check_and_downgrade_premium

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me", response_model=list[NotificationResponse])
async def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get notifications for current user."""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(100).all()
    return notifications


@router.post("/check-expiry")
async def check_premium_expiry_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create expiry warning notification if premium is close to expiry."""
    expired = check_and_downgrade_premium(db, current_user)

    if expired:
        return {
            "message": "Premium already expired. Expiry notification created.",
            "days_left": 0,
            "notification_created": True,
        }

    if not current_user.is_premium or not current_user.premium_expiry:
        return {
            "message": "No active premium subscription.",
            "days_left": None,
            "notification_created": False,
        }

    days_left = (current_user.premium_expiry - datetime.utcnow()).total_seconds() / 86400

    if days_left > 3:
        return {
            "message": "Premium subscription is active.",
            "days_left": round(days_left, 1),
            "notification_created": False,
        }

    if days_left < 0:
        return {
            "message": "Premium already expired.",
            "days_left": 0,
            "notification_created": False,
        }

    existing = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.notification_type == "premium_expiry_warning",
        Notification.is_read == False,
    ).first()

    if existing:
        return {
            "message": "Expiry warning already exists.",
            "days_left": round(days_left, 1),
            "notification_created": False,
        }

    notification = Notification(
        user_id=current_user.id,
        title="Premium Expiry Reminder",
        message=f"Your premium membership expires in {int(round(days_left))} day(s). Renew to stay featured.",
        notification_type="premium_expiry_warning",
    )
    db.add(notification)
    db.commit()

    log_action("Premium expiry warning created", user_id=current_user.id)

    return {
        "message": "Expiry warning created.",
        "days_left": round(days_left, 1),
        "notification_created": True,
    }


@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()

    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()

    return {"message": "All notifications marked as read"}
