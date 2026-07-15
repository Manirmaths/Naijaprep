from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine, ensure_schema
from app import models  # noqa: F401 -- ensure models are registered before create_all
from app.routers import auth, subjects, quiz, dashboard, review, admin, leaderboard, blitz, mock, achievements

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


@app.get("/api/health")
def health():
    return {"status": "ok"}
