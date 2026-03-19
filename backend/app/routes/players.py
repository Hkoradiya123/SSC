from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate, CareerStatsUpdate
from app.middleware.auth import get_current_user
from app.utils.premium import check_and_downgrade_premium
from app.utils.logger import log_action

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("/me", response_model=UserResponse)
async def get_current_player(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current logged-in player's profile"""
    check_and_downgrade_premium(db, current_user)
    db.refresh(current_user)
    log_action("Viewed own profile", user_id=current_user.id)
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_player(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current player's profile"""
    
    if user_update.name:
        current_user.name = user_update.name
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    if user_update.jersey_number is not None:
        current_user.jersey_number = user_update.jersey_number
    
    db.commit()
    db.refresh(current_user)
    
    log_action("Updated profile", user_id=current_user.id)
    return current_user


@router.put("/me/career-stats", response_model=UserResponse)
async def update_career_stats(
    stats_update: CareerStatsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current player's career statistics"""

    if stats_update.runs is not None:
        if stats_update.runs < 0:
            raise HTTPException(status_code=400, detail="Runs cannot be negative")
        current_user.runs = stats_update.runs

    if stats_update.matches is not None:
        if stats_update.matches < 0:
            raise HTTPException(status_code=400, detail="Matches cannot be negative")
        current_user.matches = stats_update.matches

    if stats_update.wickets is not None:
        if stats_update.wickets < 0:
            raise HTTPException(status_code=400, detail="Wickets cannot be negative")
        current_user.wickets = stats_update.wickets

    if stats_update.centuries is not None:
        if stats_update.centuries < 0:
            raise HTTPException(status_code=400, detail="Centuries cannot be negative")
        current_user.centuries = stats_update.centuries

    if stats_update.half_centuries is not None:
        if stats_update.half_centuries < 0:
            raise HTTPException(status_code=400, detail="Half-centuries cannot be negative")
        current_user.half_centuries = stats_update.half_centuries

    if stats_update.highest_score is not None:
        if stats_update.highest_score < 0:
            raise HTTPException(status_code=400, detail="Highest score cannot be negative")
        current_user.highest_score = stats_update.highest_score

    if current_user.matches > 0:
        current_user.average_runs = round(current_user.runs / current_user.matches, 2)
    else:
        current_user.average_runs = 0.0

    db.commit()
    db.refresh(current_user)

    log_action("Updated career stats", user_id=current_user.id)
    return current_user


@router.get("", response_model=List[UserResponse])
async def list_all_players(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get list of all active players"""

    players = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    for player in players:
        check_and_downgrade_premium(db, player)

    return players


@router.get("/premium", response_model=List[UserResponse])
async def get_premium_players(db: Session = Depends(get_db)):
    """Get list of premium players"""

    premium_players = db.query(User).filter(
        User.is_premium == True,
        User.is_active == True
    ).order_by(User.runs.desc()).all()

    for player in premium_players:
        check_and_downgrade_premium(db, player)

    return premium_players


@router.get("/leaderboard/top-performers", response_model=List[UserResponse])
async def get_top_performers(limit: int = 10, db: Session = Depends(get_db)):
    """Get top performers by runs"""

    top_players = db.query(User).filter(User.is_active == True).order_by(
        User.runs.desc()
    ).limit(limit).all()

    return top_players


@router.get("/leaderboard/by-wickets", response_model=List[UserResponse])
async def get_top_wicket_takers(limit: int = 10, db: Session = Depends(get_db)):
    """Get top wicket takers"""

    top_wicket_takers = db.query(User).filter(User.is_active == True).order_by(
        User.wickets.desc()
    ).limit(limit).all()

    return top_wicket_takers


@router.get("/{player_id}", response_model=UserResponse)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get player profile by ID"""
    
    player = db.query(User).filter(User.id == player_id).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    check_and_downgrade_premium(db, player)
    db.refresh(player)
    
    return player
