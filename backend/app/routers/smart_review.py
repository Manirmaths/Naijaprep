import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Question, QuizAttempt, QuestionMastery, User
from app.schemas import SmartReviewStartIn, QuizAttemptOut
from app.routers.quiz import _attempt_out, _time_limit_for

router = APIRouter(prefix="/api/smart-review", tags=["smart-review"])

# Adaptive practice / spaced repetition: pulls whatever's actually "due" per
# QuestionMastery (see models.py -- Leitner-box style), prioritizing the
# lowest boxes (most recently missed) first, then tops up with never-seen
# questions if there aren't enough due yet. Reuses the same QuizAttempt /
# answer / results flow as every other mode (see routers/quiz.py).
DEFAULT_COUNT = 15
MIN_COUNT = 5
MAX_COUNT = 40


@router.get("/due-count")
def due_count(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.utcnow()
    count = (
        db.query(QuestionMastery)
        .join(Question, Question.id == QuestionMastery.question_id)
        .filter(
            QuestionMastery.user_id == user.id,
            QuestionMastery.next_review_at <= now,
            Question.status == "active",
        )
        .count()
    )
    return {"due_count": count}


@router.post("/start", response_model=QuizAttemptOut)
def start_smart_review(
    payload: SmartReviewStartIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    n = max(MIN_COUNT, min(payload.n or DEFAULT_COUNT, MAX_COUNT))
    now = datetime.utcnow()

    due_rows = (
        db.query(QuestionMastery)
        .join(Question, Question.id == QuestionMastery.question_id)
        .filter(
            QuestionMastery.user_id == user.id,
            QuestionMastery.next_review_at <= now,
            Question.status == "active",
        )
        .order_by(QuestionMastery.box.asc(), QuestionMastery.next_review_at.asc())
        .limit(n)
        .all()
    )
    question_ids = [row.question_id for row in due_rows]

    if len(question_ids) < n:
        seen_ids = [
            qid for (qid,) in (
                db.query(QuestionMastery.question_id).filter(QuestionMastery.user_id == user.id).all()
            )
        ]
        unseen_pool = (
            db.query(Question)
            .filter(Question.status == "active", ~Question.id.in_(seen_ids or [0]))
            .all()
        )
        random.shuffle(unseen_pool)
        for q in unseen_pool:
            if len(question_ids) >= n:
                break
            question_ids.append(q.id)

    if not question_ids:
        raise HTTPException(
            status_code=400,
            detail="Nothing to review yet -- answer some questions first so Smart Review has something to work with.",
        )

    random.shuffle(question_ids)

    attempt = QuizAttempt(
        user_id=user.id,
        mode="smart_review",
        subject=None,
        topic=None,
        question_ids=question_ids,
        current_index=0,
        score=0,
        time_limit_seconds=_time_limit_for(len(question_ids)),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return _attempt_out(db, attempt)
