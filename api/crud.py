from sqlalchemy.orm import Session

from . import models


def get_torrent(db: Session, torrent_id: int):
    return db.query(models.Torrent).filter(models.Torrent.id == torrent_id).first()


def get_torrent_by_name(db: Session, name: str):
    return db.query(models.Torrent).filter(models.Torrent.name == name).first()


def get_torrents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Torrent).offset(skip).limit(limit).all()

