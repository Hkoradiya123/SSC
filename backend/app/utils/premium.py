from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, Notification
from app.config import settings
import pytz


def check_and_downgrade_premium(db: Session, user: User):
    """Check if premium membership has expired and downgrade if needed"""
    if user.is_premium and user.premium_expiry:
        if datetime.utcnow() >= user.premium_expiry:
            user.is_premium = False
            user.premium_expiry = None
            db.commit()
            
            # Create notification
            notification = Notification(
                user_id=user.id,
                title="Premium Membership Expired",
                message="Your premium membership has expired. Upgrade again to get featured!",
                notification_type="premium_expiry"
            )
            db.add(notification)
            db.commit()
            return True
    return False


def upgrade_to_premium(db: Session, user: User, days: int = 30):
    """Upgrade user to premium membership"""
    user.is_premium = True
    user.premium_start_date = datetime.utcnow()
    user.premium_expiry = datetime.utcnow() + timedelta(days=days)
    db.commit()
    
    # Create notification
    notification = Notification(
        user_id=user.id,
        title="🎉 Welcome to Premium!",
        message=f"You are now a premium member for {days} days! Enjoy exclusive features.",
        notification_type="achievement"
    )
    db.add(notification)
    db.commit()


def calculate_average_runs(db: Session, user: User) -> float:
    """Calculate average runs for a player"""
    if user.matches == 0:
        return 0.0
    return round(user.runs / user.matches, 2)


def get_player_rank(db: Session, user_id: int) -> int:
    """Get player's rank based on runs"""
    users = db.query(User).order_by(User.runs.desc()).all()
    for idx, user in enumerate(users, 1):
        if user.id == user_id:
            return idx
    return 0
