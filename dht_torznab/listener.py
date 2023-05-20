import asyncio
import binascii
import json
import re
from typing import Any

import greenstalk
from sqlalchemy import Function, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from dht_torznab import db, models, settings

MAX_PARALLEL_COROUTINES = 2


TOKEN_SEPERATOR_REGEX = re.compile(r"\W+")


# FIXME: generate this natively in PG?
def build_pgsql_search_vector(torrent_name: str) -> Function[Any]:
    token_list = TOKEN_SEPERATOR_REGEX.split(torrent_name)

    return func.to_tsvector(models.PGSQL_DICTIONARY, " ".join(token_list))


async def insert_torrent(session: AsyncSession, torrent: dict[str, Any]) -> int:
    torrent_insert_statement = (
        insert(models.TorrentsModel)
        .values(
            name=torrent["name"],
            info_hash=binascii.unhexlify(torrent["infoHash"]),
            search_vector=build_pgsql_search_vector(torrent["name"]),
        )
        .on_conflict_do_update(
            constraint=models.UNIQUE_INFO_HASH_CONSTRAINT_NAME,
            set_={"occurence_count": models.TorrentsModel.occurence_count + 1},
        )
        .returning(models.TorrentsModel.id)
    )
    result = await session.execute(torrent_insert_statement)

    return result.one().id


async def insert_files(
    session: AsyncSession,
    torrent_id: int,
    files: list[dict[str, Any]],
) -> None:
    await session.execute(
        insert(models.FilesModel),
        [
            {
                "path": file["path"],
                "size": file["size"],
                "torrent_id": torrent_id,
            }
            for file in files
        ],
    )


async def insert_torrent_in_db(torrent: dict[str, Any]) -> None:
    async with db.Session.begin() as session:
        torrent_id = await insert_torrent(session, torrent)

        await insert_files(session, torrent_id, torrent["files"])

        await session.commit()


async def process_job(client: greenstalk.Client) -> None:
    job = client.reserve()
    # TODO pydantic validation?
    torrent = json.loads(job.body)

    print(torrent)

    await insert_torrent_in_db(torrent)

    client.delete(job)


async def main() -> None:
    url = settings.get_settings().BEANSTALKD_URL

    print(f"Listening to {url}")
    tube = url.path.lstrip("/") if url.path else greenstalk.DEFAULT_TUBE

    with greenstalk.Client(
        (url.host, url.port),
        use=tube,
        watch=tube,
    ) as client:
        # TODO signal handling
        while True:
            await asyncio.gather(
                *[process_job(client) for _ in range(MAX_PARALLEL_COROUTINES)],
            )


if __name__ == "__main__":
    asyncio.run(main())
