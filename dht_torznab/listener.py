import asyncio
import binascii
import json

import greenstalk
from sqlalchemy.dialects.postgresql import insert

from dht_torznab import db, models, settings

MAX_PARALLEL_COROUTINES = 2


async def insert_torrent_in_db(torrent: dict) -> None:
    async with db.Session.begin() as transaction:
        insert_statement = (
            insert(models.Torrent)
            .values(
                name=torrent["name"],
                info_hash=binascii.unhexlify(torrent["infoHash"]),
            )
            .on_conflict_do_update(
                constraint=models.UNIQUE_INFO_HASH_CONSTRAINT_NAME,
                set_={"occurence_count": models.Torrent.occurence_count + 1},
            )
        )
        await transaction.execute(insert_statement)
        await transaction.commit()


async def process_job(client: greenstalk.Client) -> None:
    job = client.reserve()
    # TODO pydantic validation?
    torrent = json.loads(job.body)

    print(torrent["name"])

    await insert_torrent_in_db(torrent)

    client.delete(job)


async def main() -> None:
    url = settings.get_settings().BEANSTALKD_URL
    tube = url.path.rstrip("/")

    with greenstalk.Client(
        (url.host, url.port),
        use=tube,
        watch=tube,
    ) as client:
        # TODO signal handling
        while True:
            await asyncio.gather(
                *[process_job(client) for i in range(MAX_PARALLEL_COROUTINES)],
            )


if __name__ == "__main__":
    asyncio.run(main())
