#!/usr/bin/env python
import json
from multiprocessing.pool import ThreadPool
from typing import Dict, Iterator, List, Union

import django
import greenstalk
from environs import Env

django.setup()

from api import models  # noqa: E402


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

    env = Env()
    env.read_env()  # read .env file, if it exists

    beanstalkd_host = env.str("BEANSTALKD_HOST", "localhost")
    beanstalkd_port = env.int("BEANSTALKD_PORT", 11300)
    beanstalkd_tube = env.str("BEANSTALKD_TUBE", "magneticod_tube")
    listener_threads = env.int("LISTENER_THREADS", 4)

    with greenstalk.Client((beanstalkd_host, beanstalkd_port)) as bs_client, ThreadPool(
        processes=listener_threads
    ) as thread_pool:
        bs_client.watch(beanstalkd_tube)

        while True:
            job = bs_client.reserve()

            thread_pool.apply_async(
                func=create_torrent, args=[job], callback=print, error_callback=print
            )
            bs_client.delete(job)
