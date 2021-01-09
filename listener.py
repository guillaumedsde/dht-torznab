from typing import Dict
from typing import Union
from typing import Iterator
from typing import List
from multiprocessing.pool import ThreadPool

import greenstalk

import json
import django

django.setup()

from api import models


def create_torrent_files(
    file_dicts: List[Dict[str, Union[str, int]]], torrent: models.Torrent
) -> Iterator[models.File]:
    for file_dict in file_dicts:
        yield models.File(**file_dict, torrent=torrent)


def create_torrent(job: greenstalk.Job):
    torrent_dict = json.loads(job.body)
    torrent = models.Torrent(
        info_hash=torrent_dict["infoHash"], name=torrent_dict["name"]
    )

    torrent.save()

    models.File.objects.bulk_create(
        list(create_torrent_files(torrent_dict["files"], torrent))
    )

    return torrent


if __name__ == "__main__":

    with greenstalk.Client(("127.0.0.1", 11300)) as bs_client, ThreadPool(
        processes=4
    ) as thread_pool:
        bs_client.watch("magneticod_tube")

        while True:
            job = bs_client.reserve()

            thread_pool.apply_async(func=create_torrent, args=[job], callback=print, error_callback=print)
            bs_client.delete(job)
