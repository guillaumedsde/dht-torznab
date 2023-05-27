import asyncio

from dht_torznab import db, models


async def _create_ddl() -> None:
    async with db.engine.begin() as connection:
        await connection.run_sync(models.Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(_create_ddl())
