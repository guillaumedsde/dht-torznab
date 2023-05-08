from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Torrent(Base):
    __tablename__ = "torrents"

    torrent_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    info_hash: Mapped[bytes]
