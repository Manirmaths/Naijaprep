from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Question, StudyPlan, User, UserResponse
from app.schemas import StudyPlanIn, StudyPlanOut, StudyPlanTask
from app.subjects import SUBJECTS

router = APIRouter(prefix="/api/study-planner", tags=["study-planner"])

DAILY_QUESTION_COUNT = 20
MAX_SUBJECTS = 4
# A topic needs at least this many attempts within a subject before the
# planner will single it out as "today's focus" -- otherwise one lucky/
# unlucky guess could steer a whole day's plan.
MIN_TOPIC_ATTEMPTS_FOR_FOCUS = 2


def _weak_topic_for_subject(db: Session, user_id: int, subject: str) -> str | None:
    rows = (
        db.query(UserResponse)
        .join(Question, Question.id == UserResponse.question_id)
        .filter(UserResponse.user_id == user_id, Question.subject == subject)
        .all()
    )
    stats: dict[str, dict] = {}
    for r in rows:
        t = r.question.topic
        s = stats.setdefault(t, {"correct": 0, "total": 0})
        s["total"] += 1
        if r.is_correct:
            s["correct"] += 1
    candidates = [(t, s) for t, s in stats.items() if s["total"] >= MIN_TOPIC_ATTEMPTS_FOR_FOCUS]
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[1]["correct"] / item[1]["total"])
    return candidates[0][0]


def _task_for_day(db: Session, user_id: int, subjects: list[str], day_offset: int, plan_date: date) -> StudyPlanTask:
    subject = subjects[day_offset % len(subjects)]
    return StudyPlanTask(
        date=plan_date.isoformat(), subject=subject,
        topic=_weak_topic_for_subject(db, user_id, subject),
        question_count=DAILY_QUESTION_COUNT,
    )


def _build_out(db: Session, user: User, plan: StudyPlan | None) -> StudyPlanOut:
    if not plan or not plan.subjects:
        return StudyPlanOut(configured=False)

    today = date.today()
    days_until_exam = (plan.exam_date - today).days if plan.exam_date else None
    today_task = _task_for_day(db, user.id, plan.subjects, 0, today)
    week = [_task_for_day(db, user.id, plan.subjects, i, today + timedelta(days=i)) for i in range(7)]

    return StudyPlanOut(
        configured=True,
        exam_date=plan.exam_date.isoformat() if plan.exam_date else None,
        subjects=plan.subjects,
        days_until_exam=days_until_exam,
        today=today_task,
        week=week,
    )


@router.get("", response_model=StudyPlanOut)
def get_plan(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    plan = db.query(StudyPlan).filter(StudyPlan.user_id == user.id).first()
    return _build_out(db, user, plan)


@router.put("", response_model=StudyPlanOut)
def set_plan(payload: StudyPlanIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not payload.subjects:
        raise HTTPException(status_code=400, detail="Choose at least one subject.")
    if len(payload.subjects) > MAX_SUBJECTS:
        raise HTTPException(status_code=400, detail=f"Choose at most {MAX_SUBJECTS} subjects.")
    if len(set(payload.subjects)) != len(payload.subjects):
        raise HTTPException(status_code=400, detail="Choose different subjects.")
    for s in payload.subjects:
        if s not in SUBJECTS:
            raise HTTPException(status_code=404, detail=f"Unknown subject: {s}")
    if payload.exam_date and payload.exam_date < date.today():
        raise HTTPException(status_code=400, detail="Exam date can't be in the past.")

    plan = db.query(StudyPlan).filter(StudyPlan.user_id == user.id).first()
    if not plan:
        plan = StudyPlan(user_id=user.id)
        db.add(plan)
    plan.exam_date = payload.exam_date
    plan.subjects = payload.subjects
    db.commit()
    db.refresh(plan)
    return _build_out(db, user, plan)
