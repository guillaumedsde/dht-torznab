import greenstalk

import json

from api import schemas
from api import models
from api import database

db_client = database.SessionLocal()

with greenstalk.Client(("127.0.0.1", 11300)) as bs_client:
    bs_client.watch("magneticod_tube")
    while True:
        job = bs_client.reserve()
        torrent_dict = json.loads(job.body)

        torrent_schema = schemas.TorrentCreate(
            info_hash=torrent_dict["infoHash"], name=torrent_dict["name"]
        )
        db_torrent = models.Torrent(**torrent_schema.dict())

        db_client.add(db_torrent)
        db_client.commit()
        db_client.refresh(db_torrent)

        print(db_torrent.id)

        for file in torrent_dict["files"]:
            file_schema = schemas.FileCreate(**file)
            db_file = models.File(**file_schema.dict(), torrent_id=db_torrent.id)
            db_client.add(db_file)
            db_client.commit()
            db_client.refresh(db_file)

        bs_client.delete(job)

# {
#     "infoHash": "37015fcca56a404ee5163f4892bc2934cf809a4a",
#     "name": "The.Great.Gatsby.2013.2160p.BluRay.HEVC.DTS-HD.MA.5.1.IVA(2xRUS.UKR.ENG).mkv",
#     "files": [
#         {
#             "size": 76148384524,
#             "path": "The.Great.Gatsby.2013.2160p.BluRay.HEVC.DTS-HD.MA.5.1.IVA(2xRUS.UKR.ENG).mkv",
#         }
#     ],
# }
