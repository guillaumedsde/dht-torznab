from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String

from sqlalchemy.orm import relationship

from .database import Base


class Torrent(Base):
    __tablename__ = "torrents"

    id = Column(Integer, primary_key=True, index=True)
    info_hash = Column(String, index=True)
    name = Column(String, index=True)

    files = relationship("File", back_populates="torrent")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, index=True)
    size = Column(BigInteger, index=True)
    torrent_id = Column(Integer, ForeignKey("torrents.id"))

    torrent = relationship("Torrent", back_populates="files")

# {'infoHash': '37015fcca56a404ee5163f4892bc2934cf809a4a', 'name': 'The.Great.Gatsby.2013.2160p.BluRay.HEVC.DTS-HD.MA.5.1.IVA(2xRUS.UKR.ENG).mkv', 'files': [{'size': 76148384524, 'path': 'The.Great.Gatsby.2013.2160p.BluRay.HEVC.DTS-HD.MA.5.1.IVA(2xRUS.UKR.ENG).mkv'}]}