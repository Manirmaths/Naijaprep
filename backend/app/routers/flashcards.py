import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Question, User
from app.schemas import FlashcardOut, FlashcardsOut

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])

# Flashcards reuse the existing question bank (front = question text, back =
# correct answer + explanation) rather than needing separately-authored
# flashcard content -- a quick-flip study mode, not scored, no QuizAttempt.
DEFAULT_COUNT = 20
MIN_POOL = 5
MAX_COUNT = 50


def _answer_text(q: Question) -> str:
    options = {"A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d}
    return f"{q.correct_option}. {options.get(q.correct_option, '')}"


@router.get("", response_model=FlashcardsOut)
def get_flashcards(
    subject: str | None = None, topic: str | None = None, n: int = DEFAULT_COUNT,
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    n = max(MIN_POOL, min(n, MAX_COUNT))
    q = db.query(Question).filter(Question.status == "active")
    if topic:
        q = q.filter(Question.topic == topic)
    elif subject:
        q = q.filter(Question.subject == subject)
    pool = q.all()

    if len(pool) < MIN_POOL:
        label = f"topic '{topic}'" if topic else (f"subject '{subject}'" if subject else "all subjects")
        raise HTTPException(status_code=400, detail=f"Not enough questions in {label} to build a flashcard set.")

    selected = random.sample(pool, min(n, len(pool)))
    items = [
        FlashcardOut(
            id=q.id, question_text=q.question_text, image_url=q.image_url,
            answer_text=_answer_text(q), explanation=q.explanation, subject=q.subject, topic=q.topic,
        )
        for q in selected
    ]
    return FlashcardsOut(items=items)
