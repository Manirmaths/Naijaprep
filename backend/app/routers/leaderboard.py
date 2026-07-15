from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User, UserResponse, Question
from app.schemas import LeaderboardOut, LeaderboardEntry
from app.subjects import SUBJECTS

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])

TOP_N = 50

# Points-per-correct-answer, kept in sync with the +10 awarded in
# routers/quiz.py -- used here to derive a subject-scoped "points" figure
# from UserResponse history, since User.points itself is a single global
# cumulative counter with no per-subject breakdown.
POINTS_PER_CORRECT = 10


@router.get("", response_model=LeaderboardOut)
def get_leaderboard(
    subject: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if subject is not None and subject not in SUBJECTS:
        raise HTTPException(status_code=404, detail="Unknown subject.")

    if subject is None:
        return _overall_leaderboard(db, user)
    return _subject_leaderboard(db, user, subject)


def _overall_leaderboard(db: Session, user: User) -> LeaderboardOut:
    top_users = (
        db.query(User)
        .order_by(User.points.desc(), User.id.asc())
        .limit(TOP_N)
        .all()
    )

    entries = [
        LeaderboardEntry(
            rank=i + 1,
            username=u.username,
            points=u.points,
            current_streak=u.current_streak,
            is_you=(u.id == user.id),
        )
        for i, u in enumerate(top_users)
    ]

    if any(e.is_you for e in entries):
        your_rank = next(e.rank for e in entries if e.is_you)
    else:
        # User isn't in the visible top N -- compute their real rank so the
        # UI can still show "You're #123" below the cut-off list.
        higher_count = db.query(User).filter(User.points > user.points).count()
        your_rank = higher_count + 1

    return LeaderboardOut(entries=entries, your_rank=your_rank, your_points=user.points)


def _subject_points_query(db: Session, subject: str):
    return (
        db.query(
            UserResponse.user_id.label("user_id"),
            (func.count(UserResponse.id) * POINTS_PER_CORRECT).label("subject_points"),
        )
        .join(Question, Question.id == UserResponse.question_id)
        .filter(Question.subject == subject, UserResponse.is_correct.is_(True))
        .group_by(UserResponse.user_id)
    )


def _subject_leaderboard(db: Session, user: User, subject: str) -> LeaderboardOut:
    ranked = (
        _subject_points_query(db, subject)
        .order_by(func.count(UserResponse.id).desc(), UserResponse.user_id.asc())
        .limit(TOP_N)
        .all()
    )

    user_ids = [row.user_id for row in ranked]
    users_by_id = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    entries = []
    for i, row in enumerate(ranked):
        u = users_by_id.get(row.user_id)
        if not u:
            continue
        entries.append(LeaderboardEntry(
            rank=i + 1,
            username=u.username,
            points=row.subject_points,
            current_streak=u.current_streak,
            is_you=(u.id == user.id),
        ))

    your_points_row = (
        _subject_points_query(db, subject).filter(UserResponse.user_id == user.id).first()
    )
    your_points = your_points_row.subject_points if your_points_row else 0

    if any(e.is_you for e in entries):
        your_rank = next(e.rank for e in entries if e.is_you)
    else:
        higher = _subject_points_query(db, subject).subquery()
        higher_count = (
            db.query(higher.c.user_id)
            .filter(higher.c.subject_points > your_points)
            .count()
        )
        your_rank = higher_count + 1

    return LeaderboardOut(entries=entries, your_rank=your_rank, your_points=your_points)
