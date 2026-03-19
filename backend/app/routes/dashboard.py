from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.database import get_db
from app.models import User, PerformanceLog, Payment, FinanceTransaction
from app.schemas import UserResponse
from app.utils.premium import check_and_downgrade_premium

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get dashboard overview stats"""

    total_players = db.query(User).filter(User.is_active == True).count()
    premium_players = db.query(User).filter(User.is_premium == True).count()
    total_matches = sum([p.matches for p in db.query(User).all()])
    total_runs = sum([p.runs for p in db.query(User).all()])

    return {
        "total_players": total_players,
        "premium_players": premium_players,
        "total_matches": total_matches,
        "total_runs": total_runs
    }


@router.get("/extended-overview")
async def get_extended_overview(db: Session = Depends(get_db)):
    """Get extended dashboard stats for real-world club overview."""
    players = db.query(User).filter(User.is_active == True, User.role == "player").all()

    total_players = len(players)
    premium_players = len([player for player in players if player.is_premium])
    total_matches = sum(player.matches for player in players)
    total_runs = sum(player.runs for player in players)
    total_wickets = sum(player.wickets for player in players)

    avg_runs_per_match = round(total_runs / total_matches, 2) if total_matches else 0.0
    premium_ratio = round((premium_players / total_players) * 100, 2) if total_players else 0.0

    top_performance = db.query(PerformanceLog).order_by(PerformanceLog.performance_rating.desc()).first()

    return {
        "total_players": total_players,
        "premium_players": premium_players,
        "total_matches": total_matches,
        "total_runs": total_runs,
        "total_wickets": total_wickets,
        "avg_runs_per_match": avg_runs_per_match,
        "premium_ratio": premium_ratio,
        "top_performance": {
            "match_date": top_performance.match_date if top_performance else None,
            "performance_rating": top_performance.performance_rating if top_performance else 0,
            "runs_scored": top_performance.runs_scored if top_performance else 0,
            "wickets_taken": top_performance.wickets_taken if top_performance else 0,
        },
    }


@router.get("/featured-players", response_model=List[UserResponse])
async def get_featured_players(db: Session = Depends(get_db)):
    """Get featured premium players"""
    
    # Get premium players, check expiry
    premium_players = db.query(User).filter(
        User.is_premium == True,
        User.is_active == True
    ).all()

    for player in premium_players:
        check_and_downgrade_premium(db, player)

    # Get only confirmed premium players, sorted by runs
    featured = db.query(User).filter(
        User.is_premium == True,
        User.is_active == True
    ).order_by(User.runs.desc()).limit(5).all()

    return featured


@router.get("/recent-players", response_model=List[UserResponse])
async def get_recent_players(db: Session = Depends(get_db)):
    """Get recently registered players"""

    recent = db.query(User).filter(
        User.is_active == True
    ).order_by(User.created_at.desc()).limit(10).all()

    return recent


@router.get("/top-stats")
async def get_top_stats(db: Session = Depends(get_db)):
    """Get top statistics"""

    top_scorer = db.query(User).filter(User.is_active == True).order_by(
        User.runs.desc()
    ).first()

    top_wicket_taker = db.query(User).filter(User.is_active == True).order_by(
        User.wickets.desc()
    ).first()

    return {
        "top_scorer": {
            "name": top_scorer.name if top_scorer else None,
            "runs": top_scorer.runs if top_scorer else 0
        },
        "top_wicket_taker": {
            "name": top_wicket_taker.name if top_wicket_taker else None,
            "wickets": top_wicket_taker.wickets if top_wicket_taker else 0
        }
    }


@router.get("/charts")
async def get_dashboard_chart_data(db: Session = Depends(get_db)):
    """Get chart-friendly dataset for player stats and match trend."""
    top_players = db.query(User).filter(User.is_active == True).order_by(User.runs.desc()).limit(6).all()

    recent_logs = db.query(PerformanceLog).order_by(PerformanceLog.match_date.desc()).limit(12).all()
    recent_logs = list(reversed(recent_logs))

    return {
        "top_players_runs": [
            {"name": player.name, "runs": player.runs} for player in top_players
        ],
        "recent_match_trend": [
            {
                "label": log.match_date.strftime("%d %b"),
                "runs": log.runs_scored,
                "wickets": log.wickets_taken,
                "rating": log.performance_rating,
            }
            for log in recent_logs
        ],
    }


@router.get("/team-ai-insights")
async def get_team_ai_insights(db: Session = Depends(get_db)):
    """Generate AI-style team summary from recent performances."""
    recent_logs = db.query(PerformanceLog).order_by(PerformanceLog.match_date.desc()).limit(30).all()

    if not recent_logs:
        return {
            "headline": "No match data available yet",
            "team_form": "insufficient_data",
            "confidence_score": 0,
            "insights": ["Log team matches to unlock AI projections."],
        }

    avg_rating = sum(log.performance_rating for log in recent_logs) / len(recent_logs)
    avg_runs = sum(log.runs_scored for log in recent_logs) / len(recent_logs)
    avg_wickets = sum(log.wickets_taken for log in recent_logs) / len(recent_logs)

    if avg_rating >= 7.5:
        team_form = "excellent"
    elif avg_rating >= 6.0:
        team_form = "stable"
    else:
        team_form = "rebuilding"

    confidence_score = int(min(100, max(0, (avg_rating * 10) + (avg_runs * 0.7) + (avg_wickets * 7))))

    insights = [
        f"Average match rating is {avg_rating:.1f}; team form is {team_form}.",
        f"Batting output is averaging {avg_runs:.1f} runs per logged innings.",
        f"Bowling impact is averaging {avg_wickets:.1f} wickets per logged innings.",
    ]

    if avg_runs < 35:
        insights.append("Batting powerplay phase needs focused improvement.")
    if avg_wickets < 1:
        insights.append("Bowling unit should optimize line/length in middle overs.")

    return {
        "headline": "AI team pulse generated",
        "team_form": team_form,
        "confidence_score": confidence_score,
        "insights": insights,
    }


@router.get("/funds-summary")
async def get_funds_summary(db: Session = Depends(get_db)):
    """Get finance summary for dashboard cards."""
    total_collected = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(
        Payment.status == "completed"
    ).scalar() or 0.0

    manual_credits = db.query(func.coalesce(func.sum(FinanceTransaction.amount), 0.0)).filter(
        FinanceTransaction.transaction_type == "credit",
        FinanceTransaction.category == "manual_credit",
    ).scalar() or 0.0

    guest_fund_spent = db.query(func.coalesce(func.sum(FinanceTransaction.amount), 0.0)).filter(
        FinanceTransaction.transaction_type == "debit",
        FinanceTransaction.category == "guest_fund",
    ).scalar() or 0.0

    all_debits = db.query(func.coalesce(func.sum(FinanceTransaction.amount), 0.0)).filter(
        FinanceTransaction.transaction_type == "debit",
    ).scalar() or 0.0

    remaining_funds = round((total_collected + manual_credits) - all_debits, 2)

    return {
        "total_collected": round(total_collected, 2),
        "manual_credits": round(manual_credits, 2),
        "guest_fund_spent": round(guest_fund_spent, 2),
        "funds_remaining": remaining_funds,
    }
