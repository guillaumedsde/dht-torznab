import asyncio
from collections.abc import Generator
from typing import Optional

import pydantic
from sqlalchemy import func, select

from dht_torznab import db, models, schemas
from dht_torznab.settings import get_settings


async def search_torrents(
    search_query: Optional[str] = None,
    limit: Optional[None] = None,
    offset: Optional[None] = None,
) -> tuple[Generator[schemas.TorrentSchema, None, None], int]:
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
        rank_function = func.ts_rank(models.TorrentsModel.search_vector, tsquery)

        statement = statement.where(
            rank_function >= get_settings().API.MIN_SEARCH_RESULT_RANK,
        ).order_by(
            rank_function.desc(),
        )

    # NOTE: this counts all torrents since no filtering is done above,
    #       this might not be desirable.
    count_statement = select(func.count()).select_from(
        models.TorrentsModel,
    )

    async with db.Session(bind=db.repeatable_read_engine) as session:
        torrent_count_result = await session.execute(count_statement)

        torrent_count = torrent_count_result.scalar_one()

        torrent_results = await session.execute(statement)

        return (
            pydantic.parse_obj_as(schemas.TorrentSchema, row._asdict())
            for row in torrent_results.all()
        ), torrent_count


if __name__ == "__main__":
    asyncio.run(search_torrents("1080p"))
