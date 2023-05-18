import asyncio
import binascii
import json
import re

import greenstalk
from sqlalchemy import Transaction, func
from sqlalchemy.dialects.postgresql import insert

from dht_torznab import db, models, settings

MAX_PARALLEL_COROUTINES = 2


TOKEN_SEPERATOR_REGEX = re.compile(r"\W+")


# FIXME: generate this natively in PG?
def build_pgsql_search_vector(torrent_name: str):
    token_list = TOKEN_SEPERATOR_REGEX.split(torrent_name)

    return func.to_tsvector(models.PGSQL_DICTIONARY, " ".join(token_list))


async def insert_torrent(transaction: Transaction, torrent: dict) -> int:
    torrent_insert_statement = (
        insert(models.Torrent)
        .values(
            name=torrent["name"],
            info_hash=binascii.unhexlify(torrent["infoHash"]),
            search_vector=build_pgsql_search_vector(torrent["name"]),
        )
        .on_conflict_do_update(
            constraint=models.UNIQUE_INFO_HASH_CONSTRAINT_NAME,
            set_={"occurence_count": models.Torrent.occurence_count + 1},
        )
        .returning(models.Torrent.torrent_id)
    )
    result = await transaction.execute(torrent_insert_statement)

    return result.one().torrent_id


async def insert_files(
    transaction: Transaction,
    torrent_id: int,
    files: list[dict],
) -> None:
    await transaction.execute(
        insert(models.File),
        [
            {
                "path": file["path"],
                "size": file["size"],
                "torrent_id": torrent_id,
            }
            for file in files
        ],
    )


async def insert_torrent_in_db(torrent: dict) -> None:
    async with db.Session.begin() as transaction:
        torrent_id = await insert_torrent(transaction, torrent)

        await insert_files(transaction, torrent_id, torrent["files"])

        await transaction.commit()


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
    tube = url.path.lstrip("/")

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
