import asyncio
from collections.abc import Generator

import pydantic
from sqlalchemy import func, select

from dht_torznab import db, models, schemas


async def search_torrents(
    search_query: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> Generator[schemas.TorrentSchema, None, None]:
    statement = (
        select(
            models.TorrentsModel.id,
            models.TorrentsModel.name,
            models.TorrentsModel.created_at,
            models.TorrentsModel.info_hash,
            func.count(models.FilesModel.torrent_id).label("file_count"),
            func.sum(models.FilesModel.size).label("size"),
        )
        .join(models.FilesModel)
        .group_by(models.TorrentsModel.id)
    )

    if limit:
        statement = statement.limit(limit)

    if offset:
        statement = statement.offset(offset)

    if search_query:
        tsquery = func.plainto_tsquery(models.PGSQL_DICTIONARY, search_query)

        statement = statement.order_by(
            func.ts_rank(models.TorrentsModel.search_vector, tsquery).desc(),
        )

    async with db.Session() as session:
        result = await session.execute(statement)

        return (
            pydantic.parse_obj_as(schemas.TorrentSchema, row._asdict())
            for row in result.all()
        )


if __name__ == "__main__":
    asyncio.run(search_torrents("1080p"))
