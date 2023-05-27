from functools import lru_cache

import pydantic


class APISettings(pydantic.BaseModel):
    MAX_PAGE_SIZE: pydantic.PositiveInt = pydantic.Field(
        50,
        description="Maximum and default page size for API pages.",
    )
    MIN_SEARCH_RESULT_RANK: float = pydantic.Field(
        0.01,
        ge=0.0,
        description=(
            "Minimum ts_rank value below which "
            "PGSQL search results will not be displayed by the torznab API."
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