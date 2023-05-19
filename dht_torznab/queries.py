import asyncio

import pydantic
from sqlalchemy import func, select

from dht_torznab import db, models, schemas


async def search_torrents(
    search_query: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[schemas.TorrentSchema]:
    statement = (
        select(
            models.Torrent.torrent_id,
            models.Torrent.name,
            models.Torrent.info_hash,
            func.count(models.File.torrent_id).label("file_count"),
            func.sum(models.File.size).label("size"),
        )
        .join(models.File)
        .group_by(models.Torrent.torrent_id)
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

        return pydantic.parse_obj_as(
            list[schemas.TorrentSchema],
            (row._asdict() for row in result.all()),
        )


if __name__ == "__main__":
    asyncio.run(search_torrents("1080p"))
