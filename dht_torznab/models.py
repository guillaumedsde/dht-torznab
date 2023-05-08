from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint


class Base(DeclarativeBase):
    pass


UNIQUE_INFO_HASH_CONSTRAINT_NAME = "unique_info_hash"


class Torrent(Base):
    torrent_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    info_hash: Mapped[bytes] = mapped_column()
    occurence_count: Mapped[int] = mapped_column(default=1)

    __tablename__ = "torrents"
    __table_args__ = (
        UniqueConstraint(info_hash, name=UNIQUE_INFO_HASH_CONSTRAINT_NAME),
    )
