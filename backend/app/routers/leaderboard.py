from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import LeaderboardOut, LeaderboardEntry

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])

TOP_N = 50


@router.get("", response_model=LeaderboardOut)
def get_leaderboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
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
