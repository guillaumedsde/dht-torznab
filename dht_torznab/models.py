import sqlalchemy
from sqlalchemy import Computed, Index
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
        Computed(f"""to_tsvector('{PGSQL_DICTIONARY}', "name")""", persisted=True),
    )

    files: Mapped[list["File"]] = relationship(back_populates="torrent")

    __tablename__ = "torrents"
    __table_args__ = (
        UniqueConstraint(info_hash, name=UNIQUE_INFO_HASH_CONSTRAINT_NAME),
        Index("idx_torrent_name_tsv", search_vector, postgresql_using="gin"),
    )


class File(Base):
    file_id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column()
    size: Mapped[int] = mapped_column(sqlalchemy.BIGINT)

    torrent_id: Mapped[int] = mapped_column(ForeignKey(Torrent.torrent_id))
    torrent: Mapped[Torrent] = relationship(Torrent, back_populates="files")

    __tablename__ = "files"
