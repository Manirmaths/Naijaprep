from datetime import datetime, date

from sqlalchemy import String, Integer, Text, Boolean, DateTime, Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_practice_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    has_taken_diagnostic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Dormant premium/subscription plumbing -- not enforced anywhere right now.
    premium_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    responses: Mapped[list["UserResponse"]] = relationship(back_populates="user")
    review_questions: Mapped[list["ReviewQuestion"]] = relationship(back_populates="user")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="user")

    @property
    def is_premium(self) -> bool:
        return bool(self.premium_until and self.premium_until > datetime.utcnow())

    def record_practice(self) -> None:
        today = date.today()
        if self.last_practice_date == today:
            return
        if self.last_practice_date and (today - self.last_practice_date).days == 1:
            self.current_streak = (self.current_streak or 0) + 1
        else:
            self.current_streak = 1
        self.last_practice_date = today
        if self.current_streak > (self.longest_streak or 0):
            self.longest_streak = self.current_streak


class Passage(Base):
    """
    A shared reading/comprehension passage (or data set) that one or more
    Questions can reference via Question.passage_id. Most questions won't
    use one -- this exists for English comprehension, data-interpretation
    sets in Geography/Economics, etc.
    """
    __tablename__ = "passage"

    id: Mapped[int] = mapped_column(primary_key=True)
    passage_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    passage_text: Mapped[str] = mapped_column(Text, nullable=False)

    questions: Mapped[list["Question"]] = relationship(back_populates="passage")


class Question(Base):
    __tablename__ = "question"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable, human-assigned business key (e.g. "MTH-0001") used for safe
    # re-runnable CSV imports. Nullable for backward compatibility with any
    # row created before this field existed, but every seeded row has one.
    question_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)

    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    subtopic: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # "easy" | "medium" | "hard"
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False, default="medium")

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Text, not String(500): inline SVG data-URIs used for self-contained
    # diagram questions can run well past 500 characters.
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    option_a: Mapped[str] = mapped_column(Text, nullable=False)
    option_b: Mapped[str] = mapped_column(Text, nullable=False)
    option_c: Mapped[str] = mapped_column(Text, nullable=False)
    option_d: Mapped[str] = mapped_column(Text, nullable=False)
    correct_option: Mapped[str] = mapped_column(String(10), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    year: Mapped[str | None] = mapped_column(String(255), nullable=True)
    exam_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)  # pipe-separated
    # "original" | "past-question" | "licensed"
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="original")
    # "active" (visible to students) | "draft" (imported but hidden)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="active")

    passage_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("passage.passage_id"), nullable=True
    )
    passage: Mapped["Passage | None"] = relationship(back_populates="questions")


class UserResponse(Base):
    __tablename__ = "user_response"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"), nullable=False)
    # Which QuizAttempt this response belongs to, if any (nullable so
    # standalone flows like the daily challenge can still log a response).
    attempt_id: Mapped[int | None] = mapped_column(ForeignKey("quiz_attempt.id"), nullable=True)
    selected_option: Mapped[str] = mapped_column(String(1), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="responses")
    question: Mapped["Question"] = relationship()


class ReviewQuestion(Base):
    __tablename__ = "review_question"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="review_questions")
    question: Mapped["Question"] = relationship()


class QuizAttempt(Base):
    """
    Server-side quiz state, replacing what used to live in a Flask server
    session. Each attempt tracks its own question list and progress, so it's
    resumable, auditable, and works cleanly with a stateless JSON API (no
    server session cookie needed for quiz state -- only the JWT auth cookie).
    """
    __tablename__ = "quiz_attempt"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)  # quiz | cbt | diagnostic | marked | daily
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)

    question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    # For CBT: parallel list of {"id": qid, "subject": subj} lives in question_ids as dicts;
    # for other modes it's a flat list of ints.
    current_index: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)

    time_limit_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_question_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="quiz_attempts")


class Payment(Base):
    """Dormant Paystack transaction log, carried over for a later re-enable."""
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    reference: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), nullable=False)
    amount_kobo: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
