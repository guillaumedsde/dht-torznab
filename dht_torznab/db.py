from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dht_torznab import settings

# an Engine, which the Session will use for connection
# resources
engine = create_async_engine(settings.get_settings().PGSQL_DSN)

repeatable_read_engine = engine.execution_options(isolation_level="REPEATABLE READ")

# a sessionmaker(), also in the same scope as the engine
Session = async_sessionmaker(engine)
