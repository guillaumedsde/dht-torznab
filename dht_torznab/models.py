from datetime import datetime

import sqlalchemy
from sqlalchemy import TIMESTAMP, Index, MetaData, event, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.schema import CreateSchema, ForeignKey, UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dht_torznab.settings import get_settings

SCHEMA_NAME = get_settings().PGSQL_SCHEMA_NAME
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


metadata = MetaData(schema=SCHEMA_NAME)

# NOTE: ignore typing until SQLA type hint this API
event.listen(
    metadata,
    "before_create",
    CreateSchema(SCHEMA_NAME),  # type: ignore[no-untyped-call]
)


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
    }
    metadata = metadata

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        # TODO: this does not seem to do anything?
        # TODO: typing
        server_onupdate=func.now(),  # type: ignore[arg-type]
    )


UNIQUE_INFO_HASH_CONSTRAINT_NAME = "unique_info_hash"
UNIQUE_TORRENT_ID_FILE_PATH_CONSTRAINT_NAME = "unique_torrent_id_file_path"
PGSQL_DICTIONARY = "pg_catalog.simple"


class TorrentsModel(Base):
    name: Mapped[str]
    info_hash: Mapped[bytes] = mapped_column()
    # TODO: check constraints for these
    occurence_count: Mapped[int] = mapped_column(default=1)
    peer_count: Mapped[int | None] = mapped_column(default=None, nullable=True)
    total_size_in_bytes: Mapped[int] = mapped_column(sqlalchemy.BIGINT)
    file_count: Mapped[int] = mapped_column()

    search_vector = mapped_column(
        TSVectorType("name", regconfig=PGSQL_DICTIONARY),
    )

    files: Mapped[list["FilesModel"]] = relationship(back_populates="torrent")

    __tablename__ = "torrents"
    __table_args__ = (
        UniqueConstraint(info_hash, name=UNIQUE_INFO_HASH_CONSTRAINT_NAME),
        Index("idx_torrent_name_tsv", search_vector, postgresql_using="gin"),
    )


class FilesModel(Base):
    path: Mapped[str] = mapped_column()
    size: Mapped[int] = mapped_column(sqlalchemy.BIGINT)

    torrent_id: Mapped[int] = mapped_column(ForeignKey(TorrentsModel.id), index=True)
    torrent: Mapped[TorrentsModel] = relationship(TorrentsModel, back_populates="files")

    __tablename__ = "files"
