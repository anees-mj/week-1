import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import configuration and models
from src.store.config import DATABASE_URL
from src.store.database import Base
from src.store.models import OrderItemModel, OrderModel, ProductModel, UserModel

# Alembic Config object
config = context.config

# Setup Python logging from alembic.ini if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Bind model metadata for autogenerate support
target_metadata = Base.metadata

# Inject database URL from config.py
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # Required for SQLite column/table alterations
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Connects asynchronously and runs migrations on the connection."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()