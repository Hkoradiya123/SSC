from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import PerformanceLog, User
from app.schemas import PerformanceLogCreate, PerformanceLogUpdate, PerformanceLogResponse
from app.middleware.auth import get_current_user
from app.utils.logger import log_action

router = APIRouter(prefix="/performance", tags=["Performance"])


def recalculate_user_career_stats(db: Session, user: User) -> None:
    """Recalculate user stats from performance logs to keep career data accurate."""
    logs = db.query(PerformanceLog).filter(PerformanceLog.user_id == user.id).all()

    user.matches = len(logs)
    user.runs = sum(log.runs_scored for log in logs)
    user.wickets = sum(log.wickets_taken for log in logs)
    user.centuries = sum(1 for log in logs if log.runs_scored >= 100)
    user.half_centuries = sum(1 for log in logs if 50 <= log.runs_scored < 100)
    user.highest_score = max([log.runs_scored for log in logs], default=0)
    user.average_runs = round(user.runs / user.matches, 2) if user.matches else 0.0


def build_ai_insights(logs: List[PerformanceLog]) -> dict:
    """Generate lightweight AI-style insights using recent performance trends."""
    if not logs:
        return {
            "headline": "No recent match data",
            "form": "insufficient_data",
            "consistency_score": 0,
            "strengths": [],
            "focus_areas": ["Log at least 3 matches to unlock AI insights"],
            "recommendations": [
                "Track match stats after each game.",
                "Add batting and bowling notes for better insights.",
            ],
        }

    recent = logs[:5]
    avg_runs = sum(item.runs_scored for item in recent) / len(recent)
    avg_wickets = sum(item.wickets_taken for item in recent) / len(recent)
    avg_rating = sum(item.performance_rating for item in recent) / len(recent)

    first_runs = recent[-1].runs_scored
    latest_runs = recent[0].runs_scored
    run_trend = latest_runs - first_runs

    if avg_rating >= 8:
        form = "hot"
    elif avg_rating >= 6:
        form = "steady"
    else:
        form = "needs_work"

    strengths = []
    focus_areas = []

    if avg_runs >= 45:
        strengths.append("Strong batting output in recent matches")
    else:
        focus_areas.append("Improve shot selection in first 20 balls")

    if avg_wickets >= 1.2:
        strengths.append("Consistent wicket-taking impact")
    else:
        focus_areas.append("Work on death-over bowling plans")

    if run_trend > 0:
        strengths.append("Positive scoring trend over last few matches")
    elif run_trend < 0:
        focus_areas.append("Recent scoring is dropping - revisit batting routine")

    consistency_score = int(min(100, max(0, (avg_rating * 10) + (avg_runs * 0.8) + (avg_wickets * 8))))

    recommendations = [
        "Schedule one focused nets session before the next fixture.",
        "Set a single-match target and review it after every innings.",
        "Track opponent-specific plans in the notes section.",
    ]

    return {
        "headline": "AI performance snapshot ready",
        "form": form,
        "consistency_score": consistency_score,
        "recent_average_runs": round(avg_runs, 2),
        "recent_average_wickets": round(avg_wickets, 2),
        "recent_average_rating": round(avg_rating, 2),
        "strengths": strengths,
        "focus_areas": focus_areas,
        "recommendations": recommendations,
    }


@router.post("", response_model=PerformanceLogResponse)
async def log_performance(
    performance: PerformanceLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a match performance"""

    if performance.runs_scored < 0 or performance.wickets_taken < 0:
        raise HTTPException(status_code=400, detail="Runs and wickets cannot be negative")

    perf_log = PerformanceLog(
        user_id=current_user.id,
        match_date=performance.match_date,
        runs_scored=performance.runs_scored,
        wickets_taken=performance.wickets_taken,
        match_type=performance.match_type,
        opponent=performance.opponent,
        performance_rating=performance.performance_rating,
        notes=performance.notes
    )

    db.add(perf_log)
    db.flush()
    recalculate_user_career_stats(db, current_user)
    db.commit()
    db.refresh(perf_log)

    log_action("Performance logged", user_id=current_user.id,
               details=f"{performance.runs_scored} runs")

    return perf_log


@router.get("/my-logs", response_model=List[PerformanceLogResponse])
async def get_my_performance_logs(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get current player's performance logs"""

    logs = db.query(PerformanceLog).filter(
        PerformanceLog.user_id == current_user.id
    ).order_by(PerformanceLog.match_date.desc()).offset(skip).limit(limit).all()

    return logs


@router.get("/match-history")
async def get_my_match_history(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db),
):
    """Get structured match history with summary for dashboard and profile views."""
    logs = db.query(PerformanceLog).filter(
        PerformanceLog.user_id == current_user.id
    ).order_by(PerformanceLog.match_date.desc()).offset(skip).limit(limit).all()

    total_runs = sum(log.runs_scored for log in logs)
    total_wickets = sum(log.wickets_taken for log in logs)
    average_rating = round(
        sum(log.performance_rating for log in logs) / len(logs), 2
    ) if logs else 0.0

    best_match = None
    if logs:
        top = max(logs, key=lambda item: (item.runs_scored + (item.wickets_taken * 20)))
        best_match = {
            "id": top.id,
            "match_date": top.match_date,
            "opponent": top.opponent,
            "runs_scored": top.runs_scored,
            "wickets_taken": top.wickets_taken,
            "performance_rating": top.performance_rating,
        }

    return {
        "summary": {
            "matches_logged": len(logs),
            "total_runs": total_runs,
            "total_wickets": total_wickets,
            "average_rating": average_rating,
            "best_match": best_match,
        },
        "logs": logs,
    }


@router.put("/{log_id}", response_model=PerformanceLogResponse)
async def update_performance_log(
    log_id: int,
    payload: PerformanceLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Edit an existing performance log for the current player."""
    perf_log = db.query(PerformanceLog).filter(
        PerformanceLog.id == log_id,
        PerformanceLog.user_id == current_user.id,
    ).first()

    if not perf_log:
        raise HTTPException(status_code=404, detail="Performance log not found")

    updates = payload.model_dump(exclude_unset=True)

    if "runs_scored" in updates and updates["runs_scored"] < 0:
        raise HTTPException(status_code=400, detail="Runs cannot be negative")
    if "wickets_taken" in updates and updates["wickets_taken"] < 0:
        raise HTTPException(status_code=400, detail="Wickets cannot be negative")

    for key, value in updates.items():
        setattr(perf_log, key, value)

    recalculate_user_career_stats(db, current_user)
    db.commit()
    db.refresh(perf_log)

    log_action("Performance log updated", user_id=current_user.id, details=f"log_id={log_id}")
    return perf_log


@router.delete("/{log_id}")
async def delete_performance_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a performance log and recalculate career stats."""
    perf_log = db.query(PerformanceLog).filter(
        PerformanceLog.id == log_id,
        PerformanceLog.user_id == current_user.id,
    ).first()

    if not perf_log:
        raise HTTPException(status_code=404, detail="Performance log not found")

    db.delete(perf_log)
    db.flush()
    recalculate_user_career_stats(db, current_user)
    db.commit()

    log_action("Performance log deleted", user_id=current_user.id, details=f"log_id={log_id}")
    return {"message": "Performance log deleted"}


@router.get("/player/{player_id}", response_model=List[PerformanceLogResponse])
async def get_player_performance_logs(
    player_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get a player's performance logs"""

    # Check if player exists
    player = db.query(User).filter(User.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    logs = db.query(PerformanceLog).filter(
        PerformanceLog.user_id == player_id
    ).order_by(PerformanceLog.match_date.desc()).offset(skip).limit(limit).all()

    return logs


@router.get("/stats/{player_id}")
async def get_player_stats(player_id: int, db: Session = Depends(get_db)):
    """Get player statistics summary"""

    player = db.query(User).filter(User.id == player_id).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    return {
        "id": player.id,
        "name": player.name,
        "runs": player.runs,
        "matches": player.matches,
        "wickets": player.wickets,
        "centuries": player.centuries,
        "half_centuries": player.half_centuries,
        "average_runs": player.average_runs,
        "highest_score": player.highest_score
    }


@router.get("/ai-insights/{player_id}")
async def get_player_ai_insights(player_id: int, db: Session = Depends(get_db)):
    """Generate AI-based performance insights from recent match logs."""
    player = db.query(User).filter(User.id == player_id).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    logs = db.query(PerformanceLog).filter(
        PerformanceLog.user_id == player_id
    ).order_by(PerformanceLog.match_date.desc()).limit(10).all()

    return {
        "player_id": player.id,
        "player_name": player.name,
        "insights": build_ai_insights(logs),
    }
