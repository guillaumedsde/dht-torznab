from datetime import timedelta
from functools import lru_cache

import pydantic


class APISettings(pydantic.BaseModel):
    MAX_PAGE_SIZE: pydantic.PositiveInt = pydantic.Field(
        50,
        description="Maximum and default page size for API pages.",
        # NOTE: the capabilities endpoint currently has this value hardcoded,
        #       this should be resolved before modifying this setting.
    )
    MIN_SEARCH_RESULT_RANK: float = pydantic.Field(
        0.01,
        ge=0.0,
        description=(
            "Minimum ts_rank value below which "
            "PGSQL search results will not be displayed by the torznab API."
        ),
    )
    KEY: pydantic.SecretStr = pydantic.Field(
        pydantic.parse_obj_as(
            pydantic.SecretStr,
            "averysecretapikey",
        ),
        description="Key for authenticating against the torznab API.",
    )


class PeerCountUpdaterSettings(pydantic.BaseModel):
    # TODO: investigate whether binding to all interfaces is necessary
    # TODO: handle IPv6?
    DHT_UDP_SERVER_HOSTNAME: str = pydantic.Field(
        "0.0.0.0",  # noqa: S104
        description="Hostname to bind the DHT's UDP server to.",
    )
    DHT_UDP_SERVER_PORT: int = pydantic.Field(
        4747,
        description="Post to bind the DHT's UDP server to.",
        ge=1,
        le=65535,
    )
    BOOTSTRAP_NODES: list[tuple[str, int]] = pydantic.Field(
        [
            ("router.utorrent.com", 6881),
            ("router.bittorrent.com", 6881),
            ("dht.transmissionbt.com", 6881),
            ("router.bitcomet.com", 6881),
            ("dht.aelitis.com", 6881),
        ],
        description=(
            "List of hostnames and port numbers for bootstraping"
            " the peer count updater's DHT node."
        ),
    )
    ASYNCIO_COROUTINES: int = pydantic.Field(
        200,
        description=(
            "Number of coroutines running concurrently to update peer counts for"
            "torrents in the database."
        ),
        ge=1,
    )
    SLEEP_WHEN_NO_RESULT: timedelta = pydantic.Field(
        timedelta(seconds=30),
        description=(
            "Time to to sleep when no torrents in DB need their peer count updated."
        ),
    )
    UPDATE_TORRENT_PEER_COUNT_EVERY: timedelta = pydantic.Field(
        timedelta(minutes=5),
        description=(
            "Torrents whose peer count was updated less than this "
            "will not have their peer count updated."
        ),
    )


class Settings(pydantic.BaseSettings):
    PGSQL_DSN: pydantic.PostgresDsn = pydantic.Field(
        pydantic.parse_obj_as(
            pydantic.PostgresDsn,
            "postgresql+asyncpg://torznab:torznab@localhost:5432/",
        ),
        description="PostgreSQL connection URL",
    )
    PGSQL_SCHEMA_NAME: str = pydantic.Field(
        "dht_torznab",
        description="Name of the PGSQL schema used for creating app's tables.",
    )
    # TODO: protocol validation?
    BEANSTALKD_URL: pydantic.AnyUrl = pydantic.Field(
        pydantic.parse_obj_as(
            pydantic.AnyUrl,
            "beanstalkd://localhost:11300/magneticod_tube",
        ),
        description="Beanstalkd connection URL",
    )

    API: APISettings = pydantic.Field(
        APISettings(),
        description="Settings for the Torznab API.",
    )

    PEER_COUNT_UPDATER: PeerCountUpdaterSettings = pydantic.Field(
        PeerCountUpdaterSettings(),
        description="Settings for the peer count updater",
    )

    class Config:
        env_prefix = "DHT_TORZNAB__"


@lru_cache
def get_settings() -> Settings:
    """Retrieve cached instance of pydantic settings object.

    Returns:
        pydantic settings object
    """
    return Settings()
