from datetime import datetime, date, timedelta

from sqlalchemy import String, Integer, Text, Boolean, DateTime, Date, ForeignKey, JSON, UniqueConstraint
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

    # Duolingo-style streak freeze: consumable inventory that auto-protects a
    # single missed day (see record_practice()). Earned every 7-day streak
    # milestone, capped so it can't be hoarded indefinitely.
    streak_freezes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    STREAK_FREEZE_CAP = 3

    # Duolingo-style daily XP goal. Stored as a points target (points are the
    # app's existing XP-equivalent, +10 per correct answer) rather than a
    # question count, since that's what's already tracked per-user.
    daily_goal: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

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
        gap = (today - self.last_practice_date).days if self.last_practice_date else None
        if gap == 1:
            self.current_streak = (self.current_streak or 0) + 1
        elif gap == 2 and (self.streak_freezes or 0) > 0:
            # Missed exactly one day -- spend a streak freeze to keep it alive,
            # same as Duolingo's streak freeze/repair. A gap of 2+ days beyond
            # this isn't covered; the streak resets like normal.
            self.streak_freezes -= 1
            self.current_streak = (self.current_streak or 0) + 1
        else:
            self.current_streak = 1
        self.last_practice_date = today
        if self.current_streak > (self.longest_streak or 0):
            self.longest_streak = self.current_streak
        if self.current_streak > 0 and self.current_streak % 7 == 0:
            self.streak_freezes = min((self.streak_freezes or 0) + 1, self.STREAK_FREEZE_CAP)


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
    mode: Mapped[str] = mapped_column(String(20), nullable=False)  # quiz | cbt | diagnostic | marked | daily | blitz | mock
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)

    question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    # For CBT: parallel list of {"id": qid, "subject": subj} lives in question_ids as dicts;
    # for other modes it's a flat list of ints.
    current_index: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)

    time_limit_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_question_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Question IDs the student has flagged "mark for review" -- only used by
    # the free-navigation Mock exam flow (routers/mock.py); quiz/blitz/
    # smart_review's linear one-question-at-a-time flow doesn't touch this.
    marked_question_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

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


class PasswordResetToken(Base):
    """
    Single-use password reset token. We store a SHA-256 hash of the token,
    never the raw value, so a DB leak alone can't be used to reset accounts.
    The raw token only ever exists in the emailed link and in-memory for the
    duration of the request that creates/consumes it.
    """
    __tablename__ = "password_reset_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship()


class UserAchievement(Base):
    """
    Records that a user has unlocked a given achievement code (see
    app/achievements.py for the registry of codes + unlock criteria).
    Persisted (rather than recomputed on the fly every time) so earned_at is
    stable and we can tell a caller which ones were *just* unlocked.
    """
    __tablename__ = "user_achievement"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship()


class QuestionMastery(Base):
    """
    Per-user, per-question spaced-repetition state (Leitner-box style).
    Box 1 = never seen or just missed (reviewed again soonest); each correct
    answer promotes to the next box (reviewed less often); any wrong answer
    drops straight back to box 1. Updated on every quiz answer (see
    routers/quiz.py answer_quiz) and read by the Smart Review mode
    (routers/smart_review.py) to prioritize whatever's actually due.
    """
    __tablename__ = "question_mastery"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"), nullable=False)

    box: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    times_seen: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    times_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    next_review_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_question_mastery_user_question"),
    )

    MAX_BOX = 5
    BOX_INTERVAL_DAYS = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}

    def record_answer(self, is_correct: bool) -> None:
        now = datetime.utcnow()
        self.times_seen = (self.times_seen or 0) + 1
        if is_correct:
            self.times_correct = (self.times_correct or 0) + 1
            self.box = min((self.box or 1) + 1, self.MAX_BOX)
        else:
            self.box = 1
        self.last_seen_at = now
        self.next_review_at = now + timedelta(days=self.BOX_INTERVAL_DAYS[self.box])


class TutorQuery(Base):
    """
    Log of AI-tutor requests. Not shown to users -- exists purely so
    routers/tutor.py can enforce a per-user daily cap and keep OpenAI cost
    bounded even if a key is misused or a bug causes runaway requests.
    """
    __tablename__ = "tutor_query"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class PushSubscription(Base):
    """
    A browser's Web Push subscription (from PushManager.subscribe()), one row
    per device/browser a user has opted into notifications on. endpoint is
    unique per subscription -- re-subscribing the same browser upserts rather
    than duplicating. See app/push.py for sending and
    routers/notifications.py for the subscribe/unsubscribe/send endpoints.
    """
    __tablename__ = "push_subscription"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    p256dh: Mapped[str] = mapped_column(String(255), nullable=False)
    auth: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship()


class StudyPlan(Base):
    """
    One row per user: their exam date + chosen subjects. Day-by-day tasks
    (routers/study_planner.py) are computed on the fly from this plus their
    existing practice history -- not stored, so they always reflect current
    weak topics rather than going stale.
    """
    __tablename__ = "study_plan"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    subjects: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship()
