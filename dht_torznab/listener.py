import asyncio
import binascii
import json
import signal

import greenstalk

from dht_torznab import db, models

MAX_PARALLEL_COROUTINES = 2

run = True


def signal_handler(signal, frame):
    global run
    print("exiting")
    run = False


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
        while run:
            await asyncio.gather(
                *[process_job(client) for i in range(MAX_PARALLEL_COROUTINES)],
            )


if __name__ == "__main__":
    # TODO better signal handling
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main())
