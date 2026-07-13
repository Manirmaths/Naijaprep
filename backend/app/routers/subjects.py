from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Question, User
from app.schemas import SubjectOut, TopicOut
from app.subjects import SUBJECTS

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    counts = dict(
        db.query(Question.subject, func.count(Question.id))
        .filter(Question.subject.in_(SUBJECTS))
        .group_by(Question.subject)
        .all()
    )
    return [SubjectOut(name=s, question_count=counts.get(s, 0)) for s in SUBJECTS]


@router.get("/{subject}/topics", response_model=list[TopicOut])
def list_topics(subject: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    if subject not in SUBJECTS:
        raise HTTPException(status_code=404, detail="Unknown subject.")
    rows = (
        db.query(Question.topic, func.count(Question.id))
        .filter(Question.subject == subject)
        .group_by(Question.topic)
        .order_by(Question.topic.asc())
        .all()
    )
    return [TopicOut(name=t, count=c) for (t, c) in rows]
