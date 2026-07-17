from datetime import datetime, time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import UserResponse, ReviewQuestion, Question, User, QuestionMastery
from app.schemas import DashboardOut, TopicStat, DailyGoalIn, UserOut, ScoreEstimate

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

POINTS_PER_CORRECT = 10
# Duolingo-style daily goal presets (in points, +10 per correct answer).
DAILY_GOAL_PRESETS = [20, 50, 100, 150]

# Minimum total answered questions before we'll show a projected score --
# below this the estimate would swing too wildly on a handful of guesses.
SCORE_ESTIMATE_MIN_ANSWERS = 30
# Shown as a range, not a single number: real UTME scoring isn't literally
# "% correct", and this is only ever based on the student's own practice
# history, so a fixed-point number would overstate how precise this is.
SCORE_ESTIMATE_SPREAD = 20
# A topic needs at least this many attempts before it's recommended --
# otherwise one unlucky guess could flag a topic unfairly.
WEAK_TOPIC_MIN_ATTEMPTS = 3
WEAK_TOPIC_MAX_RESULTS = 3


@router.get("", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    responses = db.query(UserResponse).filter(UserResponse.user_id == user.id).all()
    stats: dict[str, dict] = {}
    subject_stats: dict[str, dict] = {}
    for r in responses:
        t = r.question.topic
        s = stats.setdefault(t, {"correct": 0, "total": 0})
        s["total"] += 1
        if r.is_correct:
            s["correct"] += 1

        subj = r.question.subject
        if subj:
            ss = subject_stats.setdefault(subj, {"correct": 0, "total": 0})
            ss["total"] += 1
            if r.is_correct:
                ss["correct"] += 1

    topic_stats = [
        TopicStat(topic=t, correct=s["correct"], total=s["total"],
                   percentage=round(s["correct"] / max(1, s["total"]) * 100, 1))
        for t, s in stats.items()
    ]

    # Weak-topic recommendations: lowest-accuracy topics with enough of a
    # sample size to mean something, worst-first.
    recommended_topics = sorted(
        (t for t in topic_stats if t.total >= WEAK_TOPIC_MIN_ATTEMPTS),
        key=lambda t: t.percentage,
    )[:WEAK_TOPIC_MAX_RESULTS]

    review_count = db.query(ReviewQuestion).filter(ReviewQuestion.user_id == user.id).count()
    exam_years = [
        y for (y,) in db.query(Question.year).filter(Question.year.isnot(None)).distinct().all()
    ]

    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    correct_today = sum(
        1 for r in responses if r.is_correct and r.timestamp and r.timestamp >= today_start
    )
    points_today = correct_today * POINTS_PER_CORRECT

    due_for_review_count = (
        db.query(QuestionMastery)
        .join(Question, Question.id == QuestionMastery.question_id)
        .filter(
            QuestionMastery.user_id == user.id,
            QuestionMastery.next_review_at <= datetime.utcnow(),
            Question.status == "active",
        )
        .count()
    )

    # Predicted JAMB score: average per-subject accuracy scaled to the
    # 400-point UTME total (4 subjects x 100), shown as a range rather than
    # a fixed number since it's an estimate from practice data, not an
    # official scoring model.
    total_answered = len(responses)
    if total_answered >= SCORE_ESTIMATE_MIN_ANSWERS and subject_stats:
        subject_pcts = [s["correct"] / s["total"] * 100 for s in subject_stats.values()]
        avg_pct = sum(subject_pcts) / len(subject_pcts)
        mid = avg_pct / 100 * 400
        score_estimate = ScoreEstimate(
            available=True,
            projected_low=max(0, round(mid - SCORE_ESTIMATE_SPREAD)),
            projected_high=min(400, round(mid + SCORE_ESTIMATE_SPREAD)),
            based_on_answers=total_answered,
        )
    else:
        remaining = max(0, SCORE_ESTIMATE_MIN_ANSWERS - total_answered)
        score_estimate = ScoreEstimate(
            available=False,
            based_on_answers=total_answered,
            message=(
                f"Answer {remaining} more question{'s' if remaining != 1 else ''} to unlock your projected score."
                if remaining else "Practice a couple more subjects to unlock your projected score."
            ),
        )

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
        recommended_topics=recommended_topics,
        due_for_review_count=due_for_review_count,
        score_estimate=score_estimate,
    )


@router.put("/daily-goal", response_model=UserOut)
def set_daily_goal(payload: DailyGoalIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.daily_goal = payload.daily_goal
    db.commit()
    db.refresh(user)
    return user
