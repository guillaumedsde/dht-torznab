import asyncio

from sqlalchemy import func, select
from sqlalchemy.orm import load_only

from dht_torznab import db, models


async def search_torrents(
    search_query: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
):  # TODO typing
    statement = select(
        models.Torrent,
    ).options(
        load_only(
            models.Torrent.torrent_id,
            models.Torrent.name,
            models.Torrent.info_hash,
        ),
    )

    if limit:
        statement = statement.limit(limit)

    if offset:
        statement = statement.offset(offset)

    if search_query:
        tsquery = func.plainto_tsquery(models.PGSQL_DICTIONARY, search_query)

        statement = statement.where(
            models.Torrent.search_vector.bool_op("@@")(tsquery),
        ).order_by(
            func.ts_rank(models.Torrent.search_vector, tsquery).desc(),
        )

    async with db.Session() as session:
        result = await session.execute(statement)

        return [result.Torrent for result in result.all()]


if __name__ == "__main__":
    asyncio.run(search_torrents("1080p"))
