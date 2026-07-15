from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    points: int
    is_admin: bool
    is_premium: bool
    current_streak: int
    longest_streak: int
    has_taken_diagnostic: bool

    class Config:
        from_attributes = True


# ---------- Subjects ----------
class SubjectOut(BaseModel):
    name: str
    question_count: int


class TopicOut(BaseModel):
    name: str
    count: int


# ---------- Passages ----------
class PassageOut(BaseModel):
    passage_id: str
    subject: Optional[str] = None
    title: Optional[str] = None
    passage_text: str

    class Config:
        from_attributes = True


# ---------- Questions / Quiz ----------
class QuestionPublic(BaseModel):
    """Question shape sent to the client BEFORE it's answered -- no correct_option."""
    id: int
    question_id: Optional[str] = None
    subject: Optional[str]
    topic: Optional[str]
    subtopic: Optional[str] = None
    difficulty: str
    question_text: str
    image_url: Optional[str] = None
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    year: Optional[str] = None
    passage: Optional[PassageOut] = None


class QuizStartIn(BaseModel):
    subject: Optional[str] = None
    topic: Optional[str] = None
    n: int = 5
    difficulty: Optional[str] = None  # easy | medium | hard
    year: Optional[str] = None
    per_q: Optional[int] = None


class BlitzStartIn(BaseModel):
    subject: str
    difficulty: Optional[str] = None  # easy | medium | hard


class MockStartIn(BaseModel):
    subjects: list[str]  # exactly 3 candidate-chosen subjects, sat alongside compulsory English


class QuizAttemptOut(BaseModel):
    attempt_id: int
    mode: str
    total: int
    current_index: int
    time_limit_seconds: Optional[int]
    per_question_seconds: Optional[int]
    current_question: Optional[QuestionPublic]
    finished: bool
    score: int


class AnswerIn(BaseModel):
    question_id: int
    selected_option: Optional[str] = None  # None/omitted = timeout / no answer


class AnswerOut(BaseModel):
    is_correct: bool
    correct_option: str
    explanation: Optional[str]
    next: QuizAttemptOut


class ResultItem(BaseModel):
    question_id: int
    question_text: str
    image_url: Optional[str] = None
    selected_option: str
    correct_option: str
    is_correct: bool
    is_marked: bool
    explanation: Optional[str] = None


class ResultsOut(BaseModel):
    score: int
    total: int
    items: list[ResultItem]


# ---------- Dashboard ----------
class TopicStat(BaseModel):
    topic: str
    correct: int
    total: int
    percentage: float


class DashboardOut(BaseModel):
    points: int
    current_streak: int
    longest_streak: int
    has_taken_diagnostic: bool
    topic_stats: list[TopicStat]
    review_count: int
    exam_years: list[str]


# ---------- Admin ----------
class QuestionIn(BaseModel):
    question_id: str = Field(min_length=1, max_length=50)
    subject: str
    topic: str
    subtopic: Optional[str] = None
    difficulty: str = "medium"  # easy | medium | hard
    exam_type: Optional[str] = None
    year: Optional[str] = None
    passage_id: Optional[str] = None
    question_text: str
    image_url: Optional[str] = None
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    explanation: Optional[str] = None
    tags: Optional[str] = None
    source: str = "original"  # original | past-question | licensed
    status: str = "active"  # active | draft


class QuestionOut(QuestionIn):
    id: int

    class Config:
        from_attributes = True


class AdminStats(BaseModel):
    total_questions: int
    total_users: int
    subjects: list[str]


# ---------- Admin: Users ----------
class AdminUserOut(BaseModel):
    id: int
    username: str
    email: str
    points: int
    is_admin: bool
    current_streak: int
    longest_streak: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Leaderboard ----------
class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    points: int
    current_streak: int
    is_you: bool


class LeaderboardOut(BaseModel):
    entries: list[LeaderboardEntry]
    your_rank: int
    your_points: int
