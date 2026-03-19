from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config import settings
from app.database import get_db
from app.models import User, Payment, FinanceTransaction
from app.middleware.auth import get_current_user
from app.schemas import GuestFundRequest, ManualCreditRequest, FinanceTransactionResponse
from app.utils.logger import log_action

router = APIRouter(prefix="/finance", tags=["Finance"])


def require_admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action",
        )


def calculate_remaining_funds(db: Session) -> float:
    total_payments = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(
        Payment.status == "completed"
    ).scalar() or 0.0

    total_manual_credits = db.query(func.coalesce(func.sum(FinanceTransaction.amount), 0.0)).filter(
        FinanceTransaction.transaction_type == "credit",
        FinanceTransaction.category == "manual_credit",
    ).scalar() or 0.0

    total_debits = db.query(func.coalesce(func.sum(FinanceTransaction.amount), 0.0)).filter(
        FinanceTransaction.transaction_type == "debit",
    ).scalar() or 0.0

    return round((total_payments + total_manual_credits) - total_debits, 2)


@router.get("/overview")
async def get_finance_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get total collected funds, pending funds, and remaining funds."""
    active_players = db.query(User).filter(User.is_active == True, User.role == "player").all()

    paid_user_ids = {
        row[0]
        for row in db.query(Payment.user_id)
        .filter(Payment.status == "completed")
        .distinct()
        .all()
    }

    unpaid_players = [player for player in active_players if player.id not in paid_user_ids]

    total_collected = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(
        Payment.status == "completed"
    ).scalar() or 0.0

    total_guest_fund_used = db.query(func.coalesce(func.sum(FinanceTransaction.amount), 0.0)).filter(
        FinanceTransaction.transaction_type == "debit",
        FinanceTransaction.category == "guest_fund",
    ).scalar() or 0.0

    pending_funds = len(unpaid_players) * settings.PREMIUM_COST
    funds_remaining = calculate_remaining_funds(db)

    return {
        "total_collected": round(total_collected, 2),
        "pending_funds": round(float(pending_funds), 2),
        "funds_remaining": funds_remaining,
        "total_guest_fund_used": round(total_guest_fund_used, 2),
        "paid_players_count": len(paid_user_ids),
        "unpaid_players_count": len(unpaid_players),
        "premium_cost_per_player": settings.PREMIUM_COST,
    }


@router.get("/player-payments")
async def get_player_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Show who paid premium and current payment status per player."""
    players = db.query(User).filter(User.is_active == True, User.role == "player").all()

    result = []
    for player in players:
        payments = db.query(Payment).filter(
            Payment.user_id == player.id,
            Payment.status == "completed",
        ).order_by(Payment.created_at.desc()).all()

        amount_paid = round(sum(payment.amount for payment in payments), 2)
        last_payment_date = payments[0].created_at if payments else None

        result.append(
            {
                "user_id": player.id,
                "name": player.name,
                "email": player.email,
                "is_premium": player.is_premium,
                "amount_paid": amount_paid,
                "has_paid": amount_paid >= settings.PREMIUM_COST,
                "last_payment_date": last_payment_date,
                "due_amount": max(0, settings.PREMIUM_COST - amount_paid),
            }
        )

    result.sort(key=lambda row: (not row["has_paid"], row["name"].lower()))
    return result


@router.get("/transactions", response_model=list[FinanceTransactionResponse])
async def get_finance_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List recent finance transactions."""
    transactions = db.query(FinanceTransaction).order_by(FinanceTransaction.created_at.desc()).limit(100).all()
    return transactions


@router.post("/guest-fund")
async def record_guest_fund_expense(
    payload: GuestFundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record guest fund expense after a match and update remaining funds."""
    require_admin(current_user)

    if payload.guest_fund <= 0:
        raise HTTPException(status_code=400, detail="Guest fund should be greater than zero")

    description = f"Match: {payload.match_name}"
    if payload.notes:
        description = f"{description} | {payload.notes}"

    transaction = FinanceTransaction(
        user_id=None,
        transaction_type="debit",
        amount=payload.guest_fund,
        category="guest_fund",
        description=description,
        reference_id=None,
    )

    db.add(transaction)
    db.commit()

    funds_remaining = calculate_remaining_funds(db)
    log_action("Guest fund expense recorded", user_id=current_user.id, details=description)

    return {
        "message": "Guest fund expense recorded",
        "debit_amount": payload.guest_fund,
        "funds_remaining": funds_remaining,
    }


@router.post("/manual-credit")
async def record_manual_credit(
    payload: ManualCreditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add manual credit to club funds."""
    require_admin(current_user)

    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Credit amount should be greater than zero")

    transaction = FinanceTransaction(
        user_id=payload.user_id,
        transaction_type="credit",
        amount=payload.amount,
        category="manual_credit",
        description=payload.notes or "Manual fund credit",
        reference_id=None,
    )

    db.add(transaction)
    db.commit()

    funds_remaining = calculate_remaining_funds(db)
    log_action("Manual fund credit recorded", user_id=current_user.id, details=str(payload.amount))

    return {
        "message": "Manual credit added",
        "credit_amount": payload.amount,
        "funds_remaining": funds_remaining,
    }
