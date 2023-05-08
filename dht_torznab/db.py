from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dht_torznab import settings

# an Engine, which the Session will use for connection
# resources
engine = create_async_engine(settings.get_settings().PGSQL_DSN)

# a sessionmaker(), also in the same scope as the engine
Session = async_sessionmaker(engine)
