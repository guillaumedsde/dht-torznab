from datetime import datetime
from typing import Optional

import sqlalchemy
from sqlalchemy import TIMESTAMP, Index, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.schema import ForeignKey, UniqueConstraint
from sqlalchemy_utils import TSVectorType


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now(),
    )


UNIQUE_INFO_HASH_CONSTRAINT_NAME = "unique_info_hash"
UNIQUE_TORRENT_ID_FILE_PATH_CONSTRAINT_NAME = "unique_torrent_id_file_path"
PGSQL_DICTIONARY = "pg_catalog.simple"


class TorrentsModel(Base):
    name: Mapped[str]
    info_hash: Mapped[bytes] = mapped_column()
    # TODO check constraints for these
    occurence_count: Mapped[int] = mapped_column(default=1)
    peer_count: Mapped[Optional[int]] = mapped_column(default=None, nullable=True)

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
