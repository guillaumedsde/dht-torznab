from typing import List

from pydantic import BaseModel


class FileBase(BaseModel):
    path: str
    size: int



class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int
    torrent_id: int

    class Config:
        orm_mode = True


class TorrentBase(BaseModel):
    info_hash: str
    name: str


class TorrentCreate(TorrentBase):
    pass


class Torrent(TorrentBase):
    id: int
    files: List[File]

    class Config:
        orm_mode = True
