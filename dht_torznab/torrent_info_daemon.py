import asyncio
from datetime import datetime, timedelta

from aiobtdht import DHT
from aioudp import UDPServer
from sqlalchemy import select, update

from dht_torznab import db, models

BOOTSTRAP_NODES = [
    ("67.215.246.10", 6881),  # router.bittorrent.com
    ("87.98.162.88", 6881),  # dht.transmissionbt.com
    ("82.221.103.244", 6881),  # router.utorrent.com
]


TD = timedelta(minutes=5)


async def bootstrap_dht_server(loop: asyncio.AbstractEventLoop) -> DHT:
    udp = UDPServer()
    udp.run("0.0.0.0", 12346, loop=loop)

    dht = DHT(
        int("0x54A10C9B159FC0FBBF6A39029BCEF406904019E0", 16),
        server=udp,
        loop=loop,
    )

    await dht.bootstrap(BOOTSTRAP_NODES)

    return dht


async def update_one_torrent_peer_count(dht_server: DHT) -> None:
    now = datetime.utcnow()

    async with db.Session.begin() as session:
        select_statement = (
            select(
                models.TorrentsModel.id,
                models.TorrentsModel.info_hash,
            )
            .with_for_update(skip_locked=True)
            .where(
                models.TorrentsModel.peer_count.is_(None)
                | (models.TorrentsModel.updated_at > (now - TD)),
            )
            .order_by(models.TorrentsModel.updated_at.desc())
            .limit(1)
        )
        result = await session.execute(select_statement)
        torrent_id, info_hash = result.one()

        peers = await dht_server[info_hash]

        peer_count = len(peers)

        print(torrent_id, info_hash, peer_count)

        update_statement = (
            update(models.TorrentsModel)
            .where(
                models.TorrentsModel.id == torrent_id,
            )
            .values(peer_count=peer_count)
        )

        result = await session.execute(update_statement)

        await session.commit()


async def main(loop: asyncio.AbstractEventLoop) -> None:
    dht_server = await bootstrap_dht_server(loop)

    while True:
        await update_one_torrent_peer_count(dht_server)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
