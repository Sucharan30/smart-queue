import os
import sys
import logging
from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from alembic import context

logger = logging.getLogger("alembic.env")

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate' support
target_metadata = Base.metadata

# Retrieve dynamic database URL from environment configuration
database_url = settings.get_database_url()
if database_url:
    # Ensure escaped percent signs in Alembic config interpolation
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url") or database_url
    if not url:
        print("\n[ERROR] DATABASE_URL is not configured.")
        print("Please set your Supabase DATABASE_URL in backend/.env before executing migrations.\n")
        sys.exit(1)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = config.get_main_option("sqlalchemy.url") or database_url
    if not url:
        print("\n[ERROR] DATABASE_URL is not configured.")
        print("Please set your Supabase DATABASE_URL in backend/.env before executing migrations.\n")
        sys.exit(1)

    # Create engine for Supabase PostgreSQL
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
