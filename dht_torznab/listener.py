import asyncio
import binascii
import json
import logging
import re
import sys
from typing import Any, cast

import greenstalk
from sqlalchemy import Function, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from dht_torznab import db, models, settings

TOKEN_SEPERATOR_REGEX = re.compile(r"\W+")


logger = logging.getLogger(__name__)


# TODO: generate this natively in PG?
def _build_pgsql_search_vector(torrent_name: str) -> Function[Any]:
    token_list = TOKEN_SEPERATOR_REGEX.split(torrent_name)

    return func.to_tsvector(models.PGSQL_DICTIONARY, " ".join(token_list))


async def _insert_torrent(session: AsyncSession, torrent: dict[str, Any]) -> int:
    torrent_insert_statement = (
        # NOTE: it seems the insert function from SQLA's PGSQL dialect is not typed
        insert(models.TorrentsModel)  # type: ignore[no-untyped-call]
        .values(
            name=torrent["name"],
            info_hash=binascii.unhexlify(torrent["infoHash"]),
            search_vector=_build_pgsql_search_vector(torrent["name"]),
        )
        .on_conflict_do_update(
            constraint=models.UNIQUE_INFO_HASH_CONSTRAINT_NAME,
            set_={"occurence_count": models.TorrentsModel.occurence_count + 1},
        )
        .returning(models.TorrentsModel.id)
    )
    result = await session.execute(torrent_insert_statement)

    # NOTE: we know our result is an int since we requested it with returning()
    return cast(int, result.one().id)


async def _insert_files(
    session: AsyncSession,
    torrent_id: int,
    files: list[dict[str, Any]],
) -> None:
    await session.execute(
        # NOTE: it seems the insert function from SQLA's PGSQL dialect is not typed
        insert(models.FilesModel),  # type: ignore[no-untyped-call]
        [
            {
                "path": file["path"],
                "size": file["size"],
                "torrent_id": torrent_id,
            }
            for file in files
        ],
    )


async def _insert_torrent_in_db(torrent: dict[str, Any]) -> None:
    async with db.Session.begin() as session:
        torrent_id = await _insert_torrent(session, torrent)

        await _insert_files(session, torrent_id, torrent["files"])

        await session.commit()


async def _process_job(client: greenstalk.Client) -> None:
    job = client.reserve()
    # TODO: pydantic validation?
    torrent = json.loads(job.body)

    logger.info(torrent["name"])

    await _insert_torrent_in_db(torrent)

    client.delete(job)


async def _main() -> None:
    url = settings.get_settings().BEANSTALKD_URL

    logger.info("Listening to %s", url)
    tube = url.path.lstrip("/") if url.path else greenstalk.DEFAULT_TUBE

    with greenstalk.Client(
        (url.host, url.port),
        use=tube,
        watch=tube,
    ) as client:
        # TODO: signal handling
        while True:
            await _process_job(client)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(_main())
