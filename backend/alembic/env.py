"""
Alembic environment configuration.

Imports all application models so autogenerate can detect schema changes,
and reads DATABASE_URL from app.config.settings instead of alembic.ini.
"""
import logging
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------------------------
# Make sure the backend/ directory is on sys.path so that `app.*` imports work
# when running `alembic` from the backend/ directory.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Base and all models so Alembic autogenerate sees the full schema.
from app.database import Base  # noqa: E402
import app.models  # noqa: E402, F401 — side-effect import registers all models

from app.config import settings  # noqa: E402

logger = logging.getLogger(__name__)

# Alembic Config object, which provides access to values within alembic.ini
config = context.config

# Override the sqlalchemy.url with the value from application settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine; calls to
    context.execute() emit the given SQL to the output.
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

    Creates an Engine and associates a connection with the context.
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
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
