from functools import lru_cache

import pydantic


class Settings(pydantic.BaseSettings):
    PGSQL_DSN: pydantic.PostgresDsn = pydantic.Field(
        "postgresql+asyncpg://torznab:torznab@localhost/",
        description="PostgreSQL connection URL",
    )
    # TODO: protocol validation?
    BEANSTALKD_URL: pydantic.AnyUrl = pydantic.Field(
        "beanstalkd://localhost:11300/magneticod_tube",
        description="Beanstalkd connection URL",
    )

    class Config:
        env_prefix = "DHT_TORZNAB__"


@lru_cache
def get_settings():
    return Settings()
