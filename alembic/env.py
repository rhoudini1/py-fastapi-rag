import sys
import os
from logging.config import fileConfig

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import Base and all models
from app.infra.database import Base
# Import all models here so Alembic can detect them
from app.infra.repositories.document import DocumentModel  # noqa: F401

# Get database URL from database.py and convert async URL to sync for Alembic
from app.infra.database import DATABASE_URL

# Convert async SQLite URL to sync URL for Alembic
def get_sync_database_url():
    """Convert async database URL to sync URL for Alembic."""
    if DATABASE_URL.startswith("sqlite+aiosqlite:///"):
        return DATABASE_URL.replace("sqlite+aiosqlite:///", "sqlite:///")
    elif DATABASE_URL.startswith("sqlite+aiosqlite://"):
        return DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
    return DATABASE_URL

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override the database URL with the converted sync URL
sync_url = get_sync_database_url()
config.set_main_option("sqlalchemy.url", sync_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Required for SQLite migrations
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
