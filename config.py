# config.py
import os
from pathlib import Path

class Config:
    # ----- SECRET KEY -----
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure")

    # ----- DATABASE URL -----
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # compute an absolute sqlite path: <repo_root>/instance/site.db
        repo_root = Path(__file__).resolve().parent
        if (repo_root / "__init__.py").exists():  # if this file is inside app/
            repo_root = repo_root.parent
        sqlite_path = repo_root / "instance" / "site.db"
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        db_url = f"sqlite:///{sqlite_path.as_posix()}"

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ----- MAIL -----
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
