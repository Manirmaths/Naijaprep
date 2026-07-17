from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Question, User
from app.schemas import PublicQuestionOut, TopStudentEntry, TopStudentsOut

router = APIRouter(prefix="/api/public", tags=["public"])

TOP_STUDENTS_N = 5


@router.get("/question-of-the-day", response_model=PublicQuestionOut)
def question_of_the_day(db: Session = Depends(get_db)):
    # No stored state: the question is picked deterministically from
    # today's date so it's stable across requests/instances all day, and
    # naturally rotates tomorrow -- ordering by id keeps the pick stable
    # even as new questions get added to the bank later.
    ids = [row[0] for row in db.query(Question.id).filter(Question.status == "active").order_by(Question.id).all()]
    if not ids:
        raise HTTPException(status_code=404, detail="No questions available.")

    today = date.today()
    q = db.get(Question, ids[today.toordinal() % len(ids)])
    return PublicQuestionOut(
        date=today.isoformat(), subject=q.subject, topic=q.topic,
        question_text=q.question_text, image_url=q.image_url,
        option_a=q.option_a, option_b=q.option_b, option_c=q.option_c, option_d=q.option_d,
        correct_option=q.correct_option, explanation=q.explanation,
    )


@router.get("/top-students", response_model=TopStudentsOut)
def top_students(db: Session = Depends(get_db)):
    top_users = (
        db.query(User)
        .order_by(User.points.desc(), User.id.asc())
        .limit(TOP_STUDENTS_N)
        .all()
    )
    entries = [
        TopStudentEntry(rank=i + 1, username=u.username, points=u.points, current_streak=u.current_streak)
        for i, u in enumerate(top_users)
    ]
    return TopStudentsOut(entries=entries)
