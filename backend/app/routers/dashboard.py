from datetime import datetime, time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import UserResponse, ReviewQuestion, Question, User
from app.schemas import DashboardOut, TopicStat, DailyGoalIn, UserOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

POINTS_PER_CORRECT = 10
# Duolingo-style daily goal presets (in points, +10 per correct answer).
DAILY_GOAL_PRESETS = [20, 50, 100, 150]


@router.get("", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    responses = db.query(UserResponse).filter(UserResponse.user_id == user.id).all()
    stats: dict[str, dict] = {}
    for r in responses:
        t = r.question.topic
        s = stats.setdefault(t, {"correct": 0, "total": 0})
        s["total"] += 1
        if r.is_correct:
            s["correct"] += 1

    topic_stats = [
        TopicStat(topic=t, correct=s["correct"], total=s["total"],
                   percentage=round(s["correct"] / max(1, s["total"]) * 100, 1))
        for t, s in stats.items()
    ]

    review_count = db.query(ReviewQuestion).filter(ReviewQuestion.user_id == user.id).count()
    exam_years = [
        y for (y,) in db.query(Question.year).filter(Question.year.isnot(None)).distinct().all()
    ]

    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    correct_today = sum(
        1 for r in responses if r.is_correct and r.timestamp and r.timestamp >= today_start
    )
    points_today = correct_today * POINTS_PER_CORRECT

    return DashboardOut(
        points=user.points,
        current_streak=user.current_streak,
        longest_streak=user.longest_streak,
        streak_freezes=user.streak_freezes,
        daily_goal=user.daily_goal,
        points_today=points_today,
        goal_met=points_today >= user.daily_goal,
        has_taken_diagnostic=user.has_taken_diagnostic,
        topic_stats=topic_stats,
        review_count=review_count,
        exam_years=exam_years,
    )


@router.put("/daily-goal", response_model=UserOut)
def set_daily_goal(payload: DailyGoalIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.daily_goal = payload.daily_goal
    db.commit()
    db.refresh(user)
    return user
