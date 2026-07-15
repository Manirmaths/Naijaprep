"""
Duolingo-style achievement badges. Each entry defines a stable `code` (used
as the DB key in UserAchievement), display copy, and a `check(db, user)`
predicate. Achievements are evaluated on-demand (see routers/achievements.py)
rather than after every answer, and persisted the first time they're earned
so earned_at stays stable and we can report which ones were *just* unlocked.
"""
from dataclasses import dataclass
from typing import Callable

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import QuizAttempt, UserResponse, User
from app.subjects import SUBJECTS


@dataclass
class Achievement:
    code: str
    title: str
    description: str
    icon: str  # Font Awesome class
    check: Callable[[Session, User], bool]


def _answered_count(db: Session, user_id: int) -> int:
    return db.query(func.count(UserResponse.id)).filter(UserResponse.user_id == user_id).scalar() or 0


def _has_finished_mode(db: Session, user_id: int, mode: str) -> bool:
    return (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id, QuizAttempt.mode == mode, QuizAttempt.finished_at.isnot(None))
        .first()
        is not None
    )


def _has_perfect_score(db: Session, user_id: int, min_questions: int = 10) -> bool:
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id, QuizAttempt.finished_at.isnot(None))
        .all()
    )
    for a in attempts:
        total = len(a.question_ids or [])
        if total >= min_questions and a.score == total:
            return True
    return False


def _subjects_with_correct_answer(db: Session, user_id: int) -> set[str]:
    rows = (
        db.query(UserResponse)
        .join(UserResponse.question)
        .filter(UserResponse.user_id == user_id, UserResponse.is_correct.is_(True))
        .all()
    )
    return {r.question.subject for r in rows if r.question.subject}


ACHIEVEMENTS: list[Achievement] = [
    Achievement(
        code="first_quiz",
        title="First Steps",
        description="Answer your first question.",
        icon="fa-solid fa-shoe-prints",
        check=lambda db, user: _answered_count(db, user.id) >= 1,
    ),
    Achievement(
        code="streak_3",
        title="On a Roll",
        description="Reach a 3-day practice streak.",
        icon="fa-solid fa-fire",
        check=lambda db, user: (user.longest_streak or 0) >= 3,
    ),
    Achievement(
        code="streak_7",
        title="Week Warrior",
        description="Reach a 7-day practice streak.",
        icon="fa-solid fa-fire-flame-curved",
        check=lambda db, user: (user.longest_streak or 0) >= 7,
    ),
    Achievement(
        code="streak_30",
        title="Unstoppable",
        description="Reach a 30-day practice streak.",
        icon="fa-solid fa-crown",
        check=lambda db, user: (user.longest_streak or 0) >= 30,
    ),
    Achievement(
        code="century",
        title="Century Club",
        description="Answer 100 questions in total.",
        icon="fa-solid fa-medal",
        check=lambda db, user: _answered_count(db, user.id) >= 100,
    ),
    Achievement(
        code="perfectionist",
        title="Perfectionist",
        description="Score 100% on a quiz of 10+ questions.",
        icon="fa-solid fa-star",
        check=lambda db, user: _has_perfect_score(db, user.id),
    ),
    Achievement(
        code="blitz_master",
        title="Blitz Master",
        description="Complete a Blitz Challenge round.",
        icon="fa-solid fa-bolt",
        check=lambda db, user: _has_finished_mode(db, user.id, "blitz"),
    ),
    Achievement(
        code="mock_marathon",
        title="Mock Marathon",
        description="Complete a Full JAMB Mock exam.",
        icon="fa-solid fa-file-signature",
        check=lambda db, user: _has_finished_mode(db, user.id, "mock"),
    ),
    Achievement(
        code="well_rounded",
        title="Well Rounded",
        description="Answer a question correctly in every subject.",
        icon="fa-solid fa-globe",
        check=lambda db, user: len(_subjects_with_correct_answer(db, user.id)) >= len(SUBJECTS),
    ),
]

ACHIEVEMENTS_BY_CODE = {a.code: a for a in ACHIEVEMENTS}
