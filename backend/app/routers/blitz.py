import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import QuizAttempt, User
from app.schemas import BlitzStartIn, QuizAttemptOut
from app.subjects import SUBJECTS
from app.routers.quiz import _pick_pool, _attempt_out

router = APIRouter(prefix="/api/blitz", tags=["blitz"])

# Blitz Challenge: fixed short timer, rapid-fire single-subject sprint.
# Reuses the same QuizAttempt model/answer/results flow as regular quizzes --
# only the mode label and time_limit_seconds differ.
BLITZ_DURATION_SECONDS = 180
BLITZ_MAX_QUESTIONS = 60


@router.post("/start", response_model=QuizAttemptOut)
def start_blitz(payload: BlitzStartIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.subject not in SUBJECTS:
        raise HTTPException(status_code=404, detail="Unknown subject.")

    pool, build = _pick_pool(db, user.id, payload.subject, None, payload.difficulty, None)

    if len(pool) < 10 and payload.difficulty is not None:
        pool = build(with_difficulty=False)

    if len(pool) < 10:
        raise HTTPException(status_code=400, detail=f"Not enough questions in {payload.subject} to start a Blitz round.")

    n = min(len(pool), BLITZ_MAX_QUESTIONS)
    selected = random.sample(pool, n)

    attempt = QuizAttempt(
        user_id=user.id,
        mode="blitz",
        subject=payload.subject,
        topic=None,
        question_ids=[q.id for q in selected],
        current_index=0,
        score=0,
        time_limit_seconds=BLITZ_DURATION_SECONDS,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return _attempt_out(db, attempt)
