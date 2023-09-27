import asyncio
import os
import sysconfig
from collections.abc import Iterable
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Connection

from alembic import context
from alembic.script import write_hooks
from dht_torznab import models
from dht_torznab.db import engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = models.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# ... etc.


def include_name(
    name: str,
    type_: str,
    parent_names: Iterable[str],  # noqa: ARG001
) -> bool:
    """Whether or not schema should be inspected when generating alembic migrations.

    Notes:
        Gotten from https://alembic.sqlalchemy.org/en/latest/autogenerate.html#omitting-schema-names-from-the-autogenerate-process

    Args:
        name: of the schema.
        type_: to check whether we are inspecting a schema
        parent_names: name of the parent DB entities?

    Returns:
        bool: whether the schema should be inspected
    """
    if type_ == "schema":
        return name == models.metadata.schema
    return True


@write_hooks.register("ruff")
def run_ruff(filename: str, options: list[str]) -> None:  # noqa: ARG001
    """Ruff hook for alembic, runs ruff on newly generated migration.

    Notes:
        Gotten from https://github.com/charliermarsh/ruff/issues/659#issuecomment-1385998994
        Once the ruff issue is resolved we should be able to remove this and simply use
        the ruff setup_script.

    Args:
        filename: Name of the migrations file.
        options: Additional options to pass to the ruff call.
    """
    ruff = Path(sysconfig.get_path("scripts")) / "ruff"
    # NOTE: spawning process without shell is acceptable
    #       since input string comes from configuration.
    os.spawnv(  # noqa: S606
        os.P_WAIT,
        ruff,
        [str(ruff), filename, "--fix", "--exit-zero"],
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
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


def do_run_migrations(connection: Connection) -> None:
    """Executes migrations with given connection.

    Args:
        connection: for executing migrations.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=target_metadata.schema,
        # NOTE: explicitely include only our schema since it is not
        #       the default one, see:
        #       https://alembic.sqlalchemy.org/en/latest/autogenerate.html#omitting-schema-names-from-the-autogenerate-process
        include_schemas=True,
        # NOTE: fix better type definition
        include_name=include_name,  # type: ignore[arg-type]
    )

    if target_metadata.schema:
        connection.execute(
            text(f"CREATE SCHEMA IF NOT EXISTS {target_metadata.schema}"),
        )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations, creates an Engine and associates a connection to context."""
    connectable = engine

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
