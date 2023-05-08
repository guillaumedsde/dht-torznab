from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# an Engine, which the Session will use for connection
# resources
engine = create_async_engine("postgresql+asyncpg://torznab:torznab@localhost/")

# a sessionmaker(), also in the same scope as the engine
Session = async_sessionmaker(engine)
