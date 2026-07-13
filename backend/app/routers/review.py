from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Question, ReviewQuestion, User
from app.schemas import QuestionOut

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("", response_model=list[QuestionOut])
def list_review(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(ReviewQuestion).filter(ReviewQuestion.user_id == user.id).all()
    return [r.question for r in rows]


@router.post("/{question_id}/mark")
def mark_review(question_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    existing = (
        db.query(ReviewQuestion)
        .filter(ReviewQuestion.user_id == user.id, ReviewQuestion.question_id == question_id)
        .first()
    )
    if existing:
        return {"status": "already_marked"}
    db.add(ReviewQuestion(user_id=user.id, question_id=question_id))
    db.commit()
    return {"status": "success"}


@router.post("/{question_id}/unmark")
def unmark_review(question_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = (
        db.query(ReviewQuestion)
        .filter(ReviewQuestion.user_id == user.id, ReviewQuestion.question_id == question_id)
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Question not marked for review.")
    db.delete(existing)
    db.commit()
    return {"status": "success"}
