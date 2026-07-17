from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai import ask_tutor
from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Question, TutorQuery, User, UserResponse
from app.schemas import TutorAskIn, TutorAskOut

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


@router.post("/ask", response_model=TutorAskOut)
def ask(payload: TutorAskIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    question = db.get(Question, payload.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    # Only allow tutoring on questions the student has already answered --
    # otherwise this endpoint could be used to fish the correct option out
    # of the AI before actually attempting the question.
    already_answered = (
        db.query(UserResponse)
        .filter(UserResponse.user_id == user.id, UserResponse.question_id == question.id)
        .first()
    )
    if not already_answered:
        raise HTTPException(status_code=403, detail="Answer this question first, then ask the tutor about it.")

    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    used_today = (
        db.query(TutorQuery)
        .filter(TutorQuery.user_id == user.id, TutorQuery.created_at >= today_start)
        .count()
    )
    if used_today >= settings.TUTOR_DAILY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"You've used all {settings.TUTOR_DAILY_LIMIT} AI tutor questions for today -- try again tomorrow.",
        )

    reply = ask_tutor(
        question_text=question.question_text,
        options={
            "A": question.option_a, "B": question.option_b,
            "C": question.option_c, "D": question.option_d,
        },
        correct_option=question.correct_option,
        explanation=question.explanation,
        user_message=payload.message,
    )

    db.add(TutorQuery(user_id=user.id, question_id=question.id))
    db.commit()

    return TutorAskOut(
        reply=reply,
        queries_remaining_today=max(0, settings.TUTOR_DAILY_LIMIT - used_today - 1),
    )
