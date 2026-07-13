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


settings = Settings()
