import random
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Question, User
from app.rate_limit import limiter
from app.schemas import GuestPracticeOut, GuestQuestionOut, PublicQuestionOut, TopStudentEntry, TopStudentsOut
from app.subjects import SUBJECTS

router = APIRouter(prefix="/api/public", tags=["public"])

TOP_STUDENTS_N = 5
GUEST_PRACTICE_MAX_N = 10


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


@router.get("/guest-practice", response_model=GuestPracticeOut)
@limiter.limit("20/minute")
def guest_practice(request: Request, subject: str, db: Session = Depends(get_db)):
    """
    A small, stateless sample of real questions for an unauthenticated
    visitor to try before signing up -- no QuizAttempt/UserResponse rows,
    no points, no streak. Deliberately not reusing routers/quiz.py's
    attempt-based flow: that flow requires a real `user_id` on QuizAttempt
    (NOT NULL in the schema), so plumbing guests through it would mean either
    a schema migration (nullable user_id) or writing throwaway rows tied to
    no real account -- both bigger changes than this feature needs. Instead
    this returns a handful of questions with the answer already included
    (same "reveal-on-click, no round trip" pattern the homepage's existing
    Question of the Day widget already uses), and the frontend hides the
    answer client-side until the visitor picks one.

    Rate-limited and capped at GUEST_PRACTICE_MAX_N per request specifically
    because -- unlike every other endpoint here -- this one has no login
    wall at all, so it's the one realistic path for someone to script a bulk
    scrape of the question bank (which is real, licensed/curated content,
    not something to give away wholesale for free).
    """
    if subject not in SUBJECTS:
        raise HTTPException(status_code=404, detail="Unknown subject.")

    pool = db.query(Question).filter(Question.status == "active", Question.subject == subject).all()
    if not pool:
        raise HTTPException(status_code=404, detail=f"No questions available for {subject} yet.")

    selected = random.sample(pool, min(GUEST_PRACTICE_MAX_N, len(pool)))
    return GuestPracticeOut(
        subject=subject,
        questions=[
            GuestQuestionOut(
                id=q.id, subject=q.subject, topic=q.topic,
                question_text=q.question_text, image_url=q.image_url,
                option_a=q.option_a, option_b=q.option_b, option_c=q.option_c, option_d=q.option_d,
                correct_option=q.correct_option, explanation=q.explanation,
            )
            for q in selected
        ],
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
