from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, Payment, FinanceTransaction
from app.schemas import PremiumUpgradeRequest, PremiumResponse, PaymentResponse
from app.middleware.auth import get_current_user
from app.utils.premium import upgrade_to_premium, check_and_downgrade_premium
from app.utils.logger import log_action, log_error
import uuid

router = APIRouter(prefix="/premium", tags=["Premium"])


@router.post("/upgrade", response_model=PremiumResponse)
async def upgrade_to_premium_plan(
    request_data: PremiumUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade player to premium membership"""
    
    if current_user.is_premium:
        # Extend premium period
        new_expiry = current_user.premium_expiry + timedelta(days=request_data.plan_days)
        current_user.premium_expiry = new_expiry
    else:
        # New premium membership
        upgrade_to_premium(db, current_user, request_data.plan_days)
    
    # Create payment record
    payment = Payment(
        user_id=current_user.id,
        amount=1000,  # ₹1000
        transaction_id=str(uuid.uuid4()),
        status="completed",
        plan_duration_days=request_data.plan_days
    )

    finance_entry = FinanceTransaction(
        user_id=current_user.id,
        transaction_type="credit",
        amount=1000,
        category="premium_payment",
        description=f"Premium payment by {current_user.email}",
        reference_id=payment.transaction_id,
    )
    
    db.add(payment)
    db.add(finance_entry)
    db.commit()
    db.refresh(current_user)
    
    log_action("Premium upgrade", user_id=current_user.id, details=f"{request_data.plan_days} days")
    
    return {
        "is_premium": current_user.is_premium,
        "premium_expiry": current_user.premium_expiry,
        "message": f"Successfully upgraded to premium for {request_data.plan_days} days!"
    }


@router.get("/status", response_model=PremiumResponse)
async def get_premium_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current premium status"""
    
    check_and_downgrade_premium(db, current_user)
    db.refresh(current_user)
    
    if current_user.is_premium:
        message = f"Premium active until {current_user.premium_expiry.strftime('%Y-%m-%d')}"
    else:
        message = "Not a premium member. Upgrade to get featured!"
    
    return {
        "is_premium": current_user.is_premium,
        "premium_expiry": current_user.premium_expiry,
        "message": message
    }


@router.post("/cancel")
async def cancel_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel premium membership"""
    
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a premium member"
        )
    
    current_user.is_premium = False
    current_user.premium_expiry = None
    db.commit()
    
    log_action("Premium cancelled", user_id=current_user.id)
    
    return {"message": "Premium membership cancelled"}


@router.get("/payments", response_model=list)
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment history"""
    
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).order_by(
        Payment.created_at.desc()
    ).all()
    
    return payments
