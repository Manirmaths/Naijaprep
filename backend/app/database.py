from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Columns added to existing models after the app was already deployed with
# real data. Base.metadata.create_all() (called on startup) only creates
# tables that don't exist yet -- it never ALTERs an existing table to add a
# new column, so on a live DB these would silently be missing and any query
# touching them (e.g. loading a User row) would fail. This patches them in,
# idempotently, on every startup. Add an entry here whenever a new column is
# added to a model that may already be deployed with data.
_PENDING_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "user": [
        ("streak_freezes", "INTEGER NOT NULL DEFAULT 0"),
        ("daily_goal", "INTEGER NOT NULL DEFAULT 50"),
    ],
}


def ensure_schema() -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table, columns in _PENDING_COLUMNS.items():
        if table not in existing_tables:
            continue  # brand-new DB -- create_all() already made it with every column
        existing_cols = {c["name"] for c in inspector.get_columns(table)}
        missing = [(name, ddl) for name, ddl in columns if name not in existing_cols]
        if not missing:
            continue
        with engine.begin() as conn:
            for name, ddl in missing:
                conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN {name} {ddl}'))
