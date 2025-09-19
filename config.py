# config.py
import os
from pathlib import Path

db_url = os.getenv("DATABASE_URL")

if not db_url:
    # Work out project root (go up if config.py is inside app/)
    repo_root = Path(__file__).resolve().parent
    if (repo_root / "__init__.py").exists():  # config.py is inside app/
        repo_root = repo_root.parent

    sqlite_path = repo_root / "instance" / "site.db"

    # ✅ Ensure the instance/ folder exists before using the DB
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    db_url = f"sqlite:///{sqlite_path.as_posix()}"

# Normalize Heroku scheme if needed
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = db_url
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure")
