# config.py (or near your app config)
import os
from pathlib import Path

db_url = os.getenv("DATABASE_URL")

if not db_url:
    # Compute absolute path to ./instance/site.db next to your repo
    repo_root = Path(__file__).resolve().parent  # adjust if config.py is inside app/
    # If config.py is in app/, go one level up:
    if (repo_root / "__init__.py").exists():
        repo_root = repo_root.parent

    sqlite_path = repo_root / "instance" / "site.db"
    db_url = f"sqlite:///{sqlite_path.as_posix()}"

# normalize old Heroku scheme just in case
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = db_url
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure")
