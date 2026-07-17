from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine, ensure_schema, normalize_emails
from app import models  # noqa: F401 -- ensure models are registered before create_all
from app.routers import (
    auth, subjects, quiz, dashboard, review, admin, leaderboard, blitz, mock, achievements,
    smart_review, tutor, notifications, study_planner, flashcards, public, notes,
)

app = FastAPI(title="Naija Prep API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    normalize_emails()


app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(quiz.router)
app.include_router(dashboard.router)
app.include_router(review.router)
app.include_router(admin.router)
app.include_router(leaderboard.router)
app.include_router(blitz.router)
app.include_router(mock.router)
app.include_router(achievements.router)
app.include_router(smart_review.router)
app.include_router(tutor.router)
app.include_router(notifications.router)
app.include_router(study_planner.router)
app.include_router(flashcards.router)
app.include_router(public.router)
app.include_router(notes.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
