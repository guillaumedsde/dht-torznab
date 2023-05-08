import asyncio
import binascii
import json

import greenstalk

from dht_torznab import db, models

MAX_PARALLEL_COROUTINES = 2


async def insert_torrent_in_db(torrent: dict) -> None:
    async with db.Session.begin() as transaction:
        transaction.add(
            models.Torrent(
                name=torrent["name"],
                info_hash=binascii.unhexlify(torrent["infoHash"]),
            ),
        )
        await transaction.commit()


async def process_job(client: greenstalk.Client) -> None:
    job = client.reserve()
    # TODO pydantic validation?
    torrent = json.loads(job.body)

    print(torrent["name"])

    await insert_torrent_in_db(torrent)

    client.delete(job)


async def main() -> None:
    with greenstalk.Client(
        ("127.0.0.1", 11300),
        use="magneticod_tube",
        watch="magneticod_tube",
    ) as client:
        # TODO signal handling
        while True:
            await asyncio.gather(
                *[process_job(client) for i in range(MAX_PARALLEL_COROUTINES)],
            )


if __name__ == "__main__":
    asyncio.run(main())
