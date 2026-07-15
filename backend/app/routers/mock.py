import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import QuizAttempt, User
from app.schemas import MockStartIn, QuizAttemptOut
from app.subjects import SUBJECTS
from app.routers.quiz import _pick_pool, _attempt_out

router = APIRouter(prefix="/api/mock", tags=["mock"])

# Full JAMB UTME mock exam: English is compulsory + 3 subjects the candidate
# picks (their combination). Real UTME format, confirmed via web search:
# 60 English questions + 40 questions per other subject = 180 total,
# single 120-minute timer for the whole exam. Reuses the same QuizAttempt
# model and the existing /api/quiz/{id}/answer + /results endpoints --
# only /start is mode-specific, same pattern as blitz.py.
ENGLISH_QUESTIONS = 60
OTHER_SUBJECT_QUESTIONS = 40
MOCK_DURATION_SECONDS = 120 * 60


@router.post("/start", response_model=QuizAttemptOut)
def start_mock(payload: MockStartIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chosen = payload.subjects or []
    if len(chosen) != 3:
        raise HTTPException(status_code=400, detail="Choose exactly 3 subjects to sit alongside English.")
    if len(set(chosen)) != 3:
        raise HTTPException(status_code=400, detail="Choose 3 different subjects.")
    if "English" in chosen:
        raise HTTPException(status_code=400, detail="English is already compulsory -- choose 3 other subjects.")
    for s in chosen:
        if s not in SUBJECTS:
            raise HTTPException(status_code=404, detail=f"Unknown subject: {s}")

    question_ids: list[int] = []
    for subject, count in [("English", ENGLISH_QUESTIONS)] + [(s, OTHER_SUBJECT_QUESTIONS) for s in chosen]:
        pool, _build = _pick_pool(db, user.id, subject, None, None, None)
        if len(pool) < count:
            raise HTTPException(status_code=400, detail=f"Not enough questions in {subject} for a full mock exam.")
        question_ids.extend(q.id for q in random.sample(pool, count))

    attempt = QuizAttempt(
        user_id=user.id,
        mode="mock",
        subject=", ".join(["English"] + chosen),
        topic=None,
        question_ids=question_ids,
        current_index=0,
        score=0,
        time_limit_seconds=MOCK_DURATION_SECONDS,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return _attempt_out(db, attempt)
