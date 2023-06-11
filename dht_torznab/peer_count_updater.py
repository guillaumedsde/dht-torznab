import asyncio
import logging
import socket
import sys

import sqlalchemy.exc
from aiobtdht import DHT
from aioudp import UDPServer
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from dht_torznab import db, models
from dht_torznab.settings import get_settings

logger = logging.getLogger(__name__)


async def _bootstrap_dht_server(loop: asyncio.AbstractEventLoop) -> DHT:
    udp = UDPServer()

    udp.run(
        get_settings().PEER_COUNT_UPDATER.DHT_UDP_SERVER_HOSTNAME,
        get_settings().PEER_COUNT_UPDATER.DHT_UDP_SERVER_PORT,
        loop=loop,
    )

    dht = DHT(
        int("0x54A10C9B159FC0FBBF6A39029BCEF406904019E0", 16),
        server=udp,
        loop=loop,
    )

    bootstrap_nodes_with_ip = []

    for host, port in get_settings().PEER_COUNT_UPDATER.BOOTSTRAP_NODES:
        try:
            bootstrap_nodes_with_ip.append((socket.gethostbyname(host), port))
        # TODO: log this
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
                | (
                    models.TorrentsModel.updated_at
                    < (
                        func.now()
                        - (
                            get_settings().PEER_COUNT_UPDATER.UPDATE_TORRENT_PEER_COUNT_EVERY
                        )
                    )
                ),
            )
            .order_by(models.TorrentsModel.updated_at.asc())
            .limit(1)
        )
        result = await session.execute(select_statement)
        try:
            torrent_id, info_hash = result.one()
        except sqlalchemy.exc.NoResultFound:
            await asyncio.sleep(
                get_settings().PEER_COUNT_UPDATER.SLEEP_WHEN_NO_RESULT.total_seconds(),
            )
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
    async with db.Session() as session:
        while True:
            await _update_one_torrent_peer_count(dht_server, session)


async def _main(loop: asyncio.AbstractEventLoop) -> None:
    dht_server = await _bootstrap_dht_server(loop)

    await asyncio.gather(
        *[
            _update_torrents_peer_count(dht_server)
            for _ in range(get_settings().PEER_COUNT_UPDATER.ASYNCIO_COROUTINES)
        ],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
    loop.run_forever()
