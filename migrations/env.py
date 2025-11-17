from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

# --- Load your Flask app & models ---
from app import create_app, db

app = create_app()
with app.app_context():
    # This is what Alembic uses to detect model changes
    target_metadata = db.metadata

# --- Alembic Config ---
config = context.config

# Option A (recommended): pull DB URL from Flask config so you don’t hardcode in alembic.ini
# This lets `alembic.ini` keep sqlalchemy.url blank.
with app.app_context():
    db_url = app.config.get("SQLALCHEMY_DATABASE_URI")
    if db_url:
        config.set_main_option("sqlalchemy.url", db_url)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# DO NOT overwrite target_metadata again
# target_metadata = None  # <-- remove this line if you had it


def include_object(object, name, type_, reflected, compare_to):
    """
    Optional: filter objects from autogenerate.
    Keep everything by default.
    """
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,        # detect column type changes
        compare_server_default=True,  # detect server default changes
    )

    with context.begin_transaction():
        context.run_migrations()


# ... imports and Flask app setup above ...

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Detect sqlite
        is_sqlite = connection.dialect.name == "sqlite"

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=is_sqlite,   # <<<< IMPORTANT for SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
