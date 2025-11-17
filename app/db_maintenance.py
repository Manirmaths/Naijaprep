# app/db_maintenance.py
from sqlalchemy import inspect, text

from app import db

INDEXES = [
    # name, table, columns tuple(s)
    ("idx_question_subject", "question", ("subject",)),
    ("idx_question_topic", "question", ("topic",)),
    ("idx_question_subject_topic", "question", ("subject", "topic")),
    ("idx_userresponse_user_question", "user_response", ("user_id", "question_id")),
]

def _index_exists(insp, table: str, name: str) -> bool:
    try:
        for ix in insp.get_indexes(table):
            if ix.get("name") == name:
                return True
    except Exception:
        # Table may not exist yet
        return False
    return False

def ensure_indexes():
    """
    Create useful indexes if missing. Safe for SQLite/Postgres/MySQL.
    Uses inspector guard instead of vendor-specific IF NOT EXISTS.
    """
    engine = db.engine
    insp = inspect(engine)

    with engine.begin() as conn:
        for ix_name, table, cols in INDEXES:
            if not _index_exists(insp, table, ix_name):
                col_list = ", ".join(cols)
                ddl = f'CREATE INDEX {ix_name} ON {table} ({col_list})'
                try:
                    conn.execute(text(ddl))
                    # Update inspector cache is not necessary—fresh process will re-read
                except Exception as e:
                    # Swallow errors from race conditions or engines that need tweaks
                    # (e.g., if index created concurrently)
                    print(f"Index create skipped ({ix_name}): {e}")
