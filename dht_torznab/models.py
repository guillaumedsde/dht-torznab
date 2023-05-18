import binascii
from urllib import parse

import sqlalchemy
from sqlalchemy import Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey, UniqueConstraint
from sqlalchemy_utils import TSVectorType


class Base(DeclarativeBase):
    pass


UNIQUE_INFO_HASH_CONSTRAINT_NAME = "unique_info_hash"
UNIQUE_TORRENT_ID_FILE_PATH_CONSTRAINT_NAME = "unique_torrent_id_file_path"
PGSQL_DICTIONARY = "pg_catalog.simple"


class Torrent(Base):
    torrent_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    info_hash: Mapped[bytes] = mapped_column()
    occurence_count: Mapped[int] = mapped_column(default=1)

    search_vector = mapped_column(
        TSVectorType("name", regconfig=PGSQL_DICTIONARY),
    )

    files: Mapped[list["File"]] = relationship(back_populates="torrent")

    __tablename__ = "torrents"
    __table_args__ = (
        UniqueConstraint(info_hash, name=UNIQUE_INFO_HASH_CONSTRAINT_NAME),
        Index("idx_torrent_name_tsv", search_vector, postgresql_using="gin"),
    )

    @property
    def str_info_hash(self) -> str:
        """Compute a string representation of the binary torrent info hash.

        Returns
        -------
            str: torrent infohash
        """
        return binascii.b2a_hex(self.info_hash).decode("utf-8")

    @property
    def magneturl(self) -> str:
        """Build the torrent magnet URL.

        Returns
        -------
            str: torrent magnet URL
        """
        url_encoded_name = parse.quote(self.name)

        return f"magnet:?xt=urn:btih:{self.str_info_hash}&dn={url_encoded_name}"


class File(Base):
    file_id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column()
    size: Mapped[int] = mapped_column(sqlalchemy.BIGINT)

    torrent_id: Mapped[int] = mapped_column(ForeignKey(Torrent.torrent_id))
    torrent: Mapped[Torrent] = relationship(Torrent, back_populates="files")

    __tablename__ = "files"
