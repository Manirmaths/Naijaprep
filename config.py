# config.py
import os
from pathlib import Path
from datetime import timedelta


class Config:
    """
    Central app configuration.

    - DATABASE_URL is honored if set; otherwise SQLite at <repo_root>/instance/site.db
    - Normalizes legacy postgres:// → postgresql://
    - Sensible security defaults for cookies and CSRF
    - Mail settings via env (Gmail-friendly defaults)
    """

    # --- Core / secrets ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me")

    # --- Database URL resolution ---
    _db_url = os.getenv("DATABASE_URL")
    if not _db_url:
        # Compute absolute sqlite path: <repo_root>/instance/site.db
        repo_root = Path(__file__).resolve().parent
        # If this file lives at project root, keep it; if moved into app/, hop up one level
        if (repo_root / "__init__.py").exists():
            repo_root = repo_root.parent

        sqlite_path = repo_root / "instance" / "site.db"
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        _db_url = f"sqlite:///{sqlite_path.as_posix()}"

    # Heroku-style legacy scheme normalization
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Optional: quieter logs in prod
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"

    # --- Mail (Gmail-friendly defaults) ---
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # --- URL / scheme hints ---
    # If you terminate TLS at a proxy (Heroku, Fly, etc.), leave https here.
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")

    # --- Cookie / session hygiene ---
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"

    # Session lifetime (server-side) for permanent sessions
    PERMANENT_SESSION_LIFETIME = timedelta(hours=6)

    # --- CSRF (Flask-WTF) ---
    WTF_CSRF_ENABLED = True
    # Time window a CSRF token remains valid (seconds)
    WTF_CSRF_TIME_LIMIT = 60 * 60  # 1 hour
    # Strict HTTPS requirement for CSRF (leave True in prod; set False only if developing over HTTP)
    WTF_CSRF_SSL_STRICT = os.getenv("WTF_CSRF_SSL_STRICT", "True").lower() == "true"
    # If you post from subdomains, you can set:
    # WTF_CSRF_TRUSTED_ORIGINS = ["https://yourdomain.com"]

    # --- Misc ---
    # Ensure Werkzeug/Flask treats proxy headers correctly if you’re behind one (optional)
    # Use ProxyFix in app factory if needed; config flag left here for completeness.
    # USE_PROXYFIX = os.getenv("USE_PROXYFIX", "False").lower() == "true"
