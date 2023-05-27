import asyncio
import logging
import socket
import sys
from datetime import timedelta

import sqlalchemy.exc
from aiobtdht import DHT
from aioudp import UDPServer
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from dht_torznab import db, models

BOOTSTRAP_NODES = [
    ("router.utorrent.com", 6881),
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.bitcomet.com", 6881),
    ("dht.aelitis.com", 6881),
]
TD = timedelta(minutes=5)
SLEEP_WHEN_NO_RESULT = timedelta(seconds=30)
PARALLEL_WORKERS = 200


logger = logging.getLogger(__name__)


async def _bootstrap_dht_server(loop: asyncio.AbstractEventLoop) -> DHT:
    udp = UDPServer()
    udp.run("0.0.0.0", 12346, loop=loop)

    dht = DHT(
        int("0x54A10C9B159FC0FBBF6A39029BCEF406904019E0", 16),
        server=udp,
        loop=loop,
    )

    bootstrap_nodes_with_ip = []

    for host, port in BOOTSTRAP_NODES:
        try:
            bootstrap_nodes_with_ip.append((socket.gethostbyname(host), port))
        # FIXME: log this
        except socket.gaierror:
            continue

    logger.info(
        "Bootrapping DHT node using the following hosts %s",
        bootstrap_nodes_with_ip,
    )
    await dht.bootstrap(bootstrap_nodes_with_ip)

    return dht


async def _update_one_torrent_peer_count(
    dht_server: DHT,
    session: AsyncSession,
) -> None:
    async with session.begin():
        select_statement = (
            select(
                models.TorrentsModel.id,
                models.TorrentsModel.info_hash,
            )
            .with_for_update(skip_locked=True)
            .where(
                models.TorrentsModel.peer_count.is_(None)
                | (models.TorrentsModel.updated_at < (func.now() - TD)),
            )
            .order_by(models.TorrentsModel.updated_at.asc())
            .limit(1)
        )
        result = await session.execute(select_statement)
        try:
            torrent_id, info_hash = result.one()
        except sqlalchemy.exc.NoResultFound:
            await asyncio.sleep(SLEEP_WHEN_NO_RESULT.total_seconds())
            return

        peers = await dht_server[info_hash]

        peer_count = len(peers)

        logger.info("torrent_id: %d peer_count: %d", torrent_id, peer_count)

        update_statement = (
            update(models.TorrentsModel)
            .where(
                models.TorrentsModel.id == torrent_id,
            )
            .values(peer_count=peer_count, updated_at=func.now())
        )

        result = await session.execute(update_statement)

        await session.commit()


async def _update_torrents_peer_count(dht_server: DHT) -> None:
    # TODO: signal handling
    while True:
        async with db.Session() as session:
            await _update_one_torrent_peer_count(dht_server, session)


async def _main(loop: asyncio.AbstractEventLoop) -> None:
    dht_server = await _bootstrap_dht_server(loop)

    await asyncio.gather(
        *[_update_torrents_peer_count(dht_server) for _ in range(PARALLEL_WORKERS)],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
    loop.run_forever()
