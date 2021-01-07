from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/torrents/", response_model=List[schemas.Torrent])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_torrents(db, skip=skip, limit=limit)
    return users


@app.get("/torrents/{torrent_id}", response_model=schemas.Torrent)
def read_user(torrent_id: int, db: Session = Depends(get_db)):
    db_torrent = crud.get_torrent(db, torrent_id=torrent_id)
    if db_torrent is None:
        raise HTTPException(status_code=404, detail="Torrent not found")
    return db_torrent
