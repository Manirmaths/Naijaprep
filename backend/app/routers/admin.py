from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import Question, Passage, User, UserResponse, ReviewQuestion, QuizAttempt, Payment
from app.schemas import QuestionIn, QuestionOut, AdminStats, PassageOut, AdminUserOut
from app.subjects import SUBJECTS

router = APIRouter(prefix="/api/admin", tags=["admin"])

VALID_DIFFICULTY = {"easy", "medium", "hard"}
VALID_SOURCE = {"original", "past-question", "licensed"}
VALID_STATUS = {"active", "draft"}


def _norm_enum(value: str, valid: set, field: str) -> str:
    v = (value or "").strip().lower()
    if v not in valid:
        raise HTTPException(status_code=400, detail=f"{field} must be one of: {', '.join(sorted(valid))}.")
    return v


def _validate_passage(db: Session, passage_id):
    pid = (passage_id or "").strip() or None
    if pid and not db.query(Passage).filter(Passage.passage_id == pid).first():
        raise HTTPException(status_code=400, detail=f"passage_id '{pid}' does not exist. Create the passage first.")
    return pid


@router.get("/stats", response_model=AdminStats)
def stats(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return AdminStats(
        total_questions=db.query(Question).count(),
        total_users=db.query(User).count(),
        subjects=SUBJECTS,
    )


@router.get("/questions", response_model=list[QuestionOut])
def list_questions(
    subject: str = None, page: int = 1, per_page: int = 25,
    db: Session = Depends(get_db), _admin: User = Depends(require_admin),
):
    q = db.query(Question)
    if subject and subject in SUBJECTS:
        q = q.filter(Question.subject == subject)
    return (
        q.order_by(Question.id.desc())
        .offset((max(page, 1) - 1) * per_page)
        .limit(per_page)
        .all()
    )


def _normalize_correct(value: str) -> str:
    v = (value or "A").strip().upper()[:1]
    return v if v in ("A", "B", "C", "D") else "A"


@router.post("/questions", response_model=QuestionOut, status_code=201)
def create_question(payload: QuestionIn, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    qid = payload.question_id.strip()
    if db.query(Question).filter(Question.question_id == qid).first():
        raise HTTPException(status_code=400, detail=f"question_id '{qid}' is already in use.")

    q = Question(
        question_id=qid,
        subject=payload.subject.strip(),
        topic=payload.topic.strip(),
        subtopic=(payload.subtopic or "").strip() or None,
        difficulty=_norm_enum(payload.difficulty, VALID_DIFFICULTY, "difficulty"),
        exam_type=(payload.exam_type or "").strip() or None,
        year=(payload.year or "").strip() or None,
        passage_id=_validate_passage(db, payload.passage_id),
        question_text=payload.question_text.strip(),
        image_url=(payload.image_url or "").strip() or None,
        option_a=payload.option_a.strip(),
        option_b=payload.option_b.strip(),
        option_c=payload.option_c.strip(),
        option_d=payload.option_d.strip(),
        correct_option=_normalize_correct(payload.correct_option),
        explanation=(payload.explanation or "").strip(),
        tags=(payload.tags or "").strip() or None,
        source=_norm_enum(payload.source, VALID_SOURCE, "source"),
        status=_norm_enum(payload.status, VALID_STATUS, "status"),
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.put("/questions/{question_id}", response_model=QuestionOut)
def update_question(question_id: int, payload: QuestionIn, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    qid = payload.question_id.strip()
    dupe = db.query(Question).filter(Question.question_id == qid, Question.id != question_id).first()
    if dupe:
        raise HTTPException(status_code=400, detail=f"question_id '{qid}' is already in use.")

    q.question_id = qid
    q.subject = payload.subject.strip()
    q.topic = payload.topic.strip()
    q.subtopic = (payload.subtopic or "").strip() or None
    q.difficulty = _norm_enum(payload.difficulty, VALID_DIFFICULTY, "difficulty")
    q.exam_type = (payload.exam_type or "").strip() or None
    q.year = (payload.year or "").strip() or None
    q.passage_id = _validate_passage(db, payload.passage_id)
    q.question_text = payload.question_text.strip()
    q.image_url = (payload.image_url or "").strip() or None
    q.option_a = payload.option_a.strip()
    q.option_b = payload.option_b.strip()
    q.option_c = payload.option_c.strip()
    q.option_d = payload.option_d.strip()
    q.correct_option = _normalize_correct(payload.correct_option)
    q.explanation = (payload.explanation or "").strip()
    q.tags = (payload.tags or "").strip() or None
    q.source = _norm_enum(payload.source, VALID_SOURCE, "source")
    q.status = _norm_enum(payload.status, VALID_STATUS, "status")
    db.commit()
    db.refresh(q)
    return q


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
    db.delete(q)
    db.commit()
    return {"status": "deleted"}


@router.get("/passages", response_model=list[PassageOut])
def list_passages(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return db.query(Passage).order_by(Passage.id.desc()).all()


@router.get("/users", response_model=list[AdminUserOut])
def list_users(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return db.query(User).order_by(User.points.desc(), User.id.asc()).all()


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="You can't delete your own account from here.")

    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")

    # Clear dependent rows first -- Postgres enforces the FK constraints,
    # so a bare delete on "user" would fail while these still reference it.
    db.query(UserResponse).filter(UserResponse.user_id == user_id).delete()
    db.query(ReviewQuestion).filter(ReviewQuestion.user_id == user_id).delete()
    db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).delete()
    db.query(Payment).filter(Payment.user_id == user_id).delete()
    db.delete(target)
    db.commit()
    return {"status": "deleted"}


@router.post("/users/{user_id}/toggle-admin", response_model=AdminUserOut)
def toggle_admin(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="You can't change your own admin status from here.")

    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")

    target.is_admin = not target.is_admin
    db.commit()
    db.refresh(target)
    return target
