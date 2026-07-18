"""
Family/guardian links (Phase 5): lets a parent, guardian, or tutor link
themselves as a read-only watcher of one or more student accounts' progress,
via a short code the student shares -- no password sharing, no elevated
access. Deliberately generic rather than a dedicated "parent" vs "teacher"
role: a tutor watching five students is just five GuardianLink rows under
one guardian_user_id, so this single feature covers both use cases without
a separate classroom/cohort data model. See models.GuardianLink for the
fuller reasoning.

Any authenticated user can both share a code (as a student) and redeem
someone else's code (as a guardian) -- there's no fixed "role" on User.
"""
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import GuardianLink, User
from app.progress import compute_progress
from app.schemas import ChildSummaryOut, LinkedChildOut, LinkIn, MyCodeOut

router = APIRouter(prefix="/api/family", tags=["family"])

CODE_LENGTH = 8


def _generate_unique_code(db: Session) -> str:
    for _ in range(10):
        code = secrets.token_hex(CODE_LENGTH // 2).upper()
        if not db.query(User).filter(User.guardian_link_code == code).first():
            return code
    # Astronomically unlikely with 4-byte hex codes, but fail loudly rather
    # than silently returning a colliding code if it ever somehow happens.
    raise HTTPException(status_code=500, detail="Could not generate a unique code. Try again.")


@router.get("/my-code", response_model=MyCodeOut)
def get_my_code(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.guardian_link_code:
        user.guardian_link_code = _generate_unique_code(db)
        db.commit()
    return MyCodeOut(code=user.guardian_link_code)


@router.post("/my-code/regenerate", response_model=MyCodeOut)
def regenerate_my_code(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Invalidates the old code -- anyone who only has the old one can no
    # longer link (existing GuardianLink rows are untouched, this only
    # affects future redemptions).
    user.guardian_link_code = _generate_unique_code(db)
    db.commit()
    return MyCodeOut(code=user.guardian_link_code)


@router.post("/link", response_model=LinkedChildOut, status_code=201)
def link_student(payload: LinkIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    code = payload.code.strip().upper()
    student = db.query(User).filter(User.guardian_link_code == code).first()
    if not student:
        raise HTTPException(status_code=404, detail="That code doesn't match any account.")
    if student.id == user.id:
        raise HTTPException(status_code=400, detail="You can't link to your own account.")

    existing = (
        db.query(GuardianLink)
        .filter(GuardianLink.guardian_user_id == user.id, GuardianLink.student_user_id == student.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail=f"You're already watching {student.username}.")

    link = GuardianLink(guardian_user_id=user.id, student_user_id=student.id)
    db.add(link)
    db.commit()
    db.refresh(link)

    return LinkedChildOut(
        id=student.id, username=student.username, current_streak=student.current_streak,
        points=student.points, linked_at=link.created_at,
    )


@router.get("/children", response_model=list[LinkedChildOut])
def list_children(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    links = db.query(GuardianLink).filter(GuardianLink.guardian_user_id == user.id).all()
    out = []
    for link in links:
        student = db.get(User, link.student_user_id)
        if not student:
            continue
        out.append(LinkedChildOut(
            id=student.id, username=student.username, current_streak=student.current_streak,
            points=student.points, linked_at=link.created_at,
        ))
    return out


@router.get("/children/{student_id}/summary", response_model=ChildSummaryOut)
def child_summary(student_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    link = (
        db.query(GuardianLink)
        .filter(GuardianLink.guardian_user_id == user.id, GuardianLink.student_user_id == student_id)
        .first()
    )
    if not link:
        # 404, not 403 -- don't confirm whether student_id exists at all to
        # a guardian who was never linked to it.
        raise HTTPException(status_code=404, detail="No linked student with that ID.")

    student = db.get(User, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="No linked student with that ID.")

    topic_stats, recommended_topics, score_estimate, _ = compute_progress(db, student.id)
    return ChildSummaryOut(
        id=student.id, username=student.username, points=student.points,
        current_streak=student.current_streak, longest_streak=student.longest_streak,
        topic_stats=topic_stats, recommended_topics=recommended_topics, score_estimate=score_estimate,
    )


@router.delete("/children/{student_id}")
def unlink_student(student_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    link = (
        db.query(GuardianLink)
        .filter(GuardianLink.guardian_user_id == user.id, GuardianLink.student_user_id == student_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="No linked student with that ID.")
    db.delete(link)
    db.commit()
    return {"status": "unlinked"}
