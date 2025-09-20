# config.py
import os
from pathlib import Path


class Config:
    """
    Central app configuration.
    - Uses DATABASE_URL if provided; otherwise stores SQLite at <repo>/instance/site.db
    - Normalizes legacy postgres:// → postgresql://
    - Mail settings pulled from env (Gmail defaults)
    """

    # --- Core / security ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure")

    # --- Database URL resolution ---
    _db_url = os.getenv("DATABASE_URL")
    if not _db_url:
        # Compute an absolute sqlite path: <repo_root>/instance/site.db
        repo_root = Path(__file__).resolve().parent
        # If this file were ever relocated inside app/, hop up one level
        if (repo_root / "__init__.py").exists():
            repo_root = repo_root.parent

        sqlite_path = repo_root / "instance" / "site.db"
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        _db_url = f"sqlite:///{sqlite_path.as_posix()}"

    # Heroku legacy scheme normalization
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Mail (Gmail-friendly defaults) ---
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # --- Optional cookie / URL hints (safe defaults for Heroku/HTTPS) ---
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() == "true"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")
