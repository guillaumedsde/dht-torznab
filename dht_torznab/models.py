import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey, UniqueConstraint


class Base(DeclarativeBase):
    pass


UNIQUE_INFO_HASH_CONSTRAINT_NAME = "unique_info_hash"
UNIQUE_TORRENT_ID_FILE_PATH_CONSTRAINT_NAME = "unique_torrent_id_file_path"


class Torrent(Base):
    torrent_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    info_hash: Mapped[bytes] = mapped_column()
    occurence_count: Mapped[int] = mapped_column(default=1)

    files: Mapped[list["File"]] = relationship(back_populates="torrent")

    __tablename__ = "torrents"
    __table_args__ = (
        UniqueConstraint(info_hash, name=UNIQUE_INFO_HASH_CONSTRAINT_NAME),
    )


class File(Base):
    file_id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column()
    size: Mapped[int] = mapped_column(sqlalchemy.BIGINT)

    torrent_id: Mapped[int] = mapped_column(ForeignKey(Torrent.torrent_id))
    torrent: Mapped[Torrent] = relationship(Torrent, back_populates="files")

    __tablename__ = "files"
