import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-insecure-secret-change-me")
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./naijaprep.db")
    FRONTEND_ORIGINS: list[str] = [
        o.strip() for o in os.environ.get("FRONTEND_ORIGINS", "http://localhost:5173").split(",") if o.strip()
    ]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    ALGORITHM: str = "HS256"
    PAYSTACK_SECRET_KEY: str = os.environ.get("PAYSTACK_SECRET_KEY", "")
    PAYSTACK_PUBLIC_KEY: str = os.environ.get("PAYSTACK_PUBLIC_KEY", "")
    IS_PRODUCTION: bool = os.environ.get("ENV", "development") == "production"

    # Transactional email (password reset) via Resend's HTTP API. Left unset
    # in dev/until configured -- app/email.py falls back to logging the
    # reset link instead of failing, so forgot-password still works locally.
    RESEND_API_KEY: str = os.environ.get("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL: str = os.environ.get("RESEND_FROM_EMAIL", "Naija Prep <noreply@naijaprep.com.ng>")
    # Base URL used to build the reset-password link sent by email.
    PUBLIC_APP_URL: str = os.environ.get(
        "PUBLIC_APP_URL",
        FRONTEND_ORIGINS[0] if FRONTEND_ORIGINS else "http://localhost:5173",
    )

    # AI tutor ("explain this differently") + admin auto-tagging, via
    # OpenAI's API. Left unset in dev/until configured -- app/ai.py falls
    # back to a friendly "not set up yet" response instead of failing, same
    # pattern as RESEND_API_KEY above.
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    # Per-user, per-day cap on AI tutor requests -- bounds OpenAI cost.
    TUTOR_DAILY_LIMIT: int = int(os.environ.get("TUTOR_DAILY_LIMIT", "30"))


settings = Settings()
