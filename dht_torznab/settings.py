from functools import lru_cache

import pydantic


class APISettings(pydantic.BaseModel):
    MAX_PAGE_SIZE: pydantic.PositiveInt = pydantic.Field(
        50,
        description="Maximum and default page size for API pages.",
    )


class Settings(pydantic.BaseSettings):
    PGSQL_DSN: pydantic.PostgresDsn = pydantic.Field(
        pydantic.parse_obj_as(
            pydantic.PostgresDsn,
            "postgresql+asyncpg://torznab:torznab@localhost/",
        ),
        description="PostgreSQL connection URL",
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

    class Config:
        env_prefix = "DHT_TORZNAB__"


@lru_cache
def get_settings() -> Settings:
    return Settings()
