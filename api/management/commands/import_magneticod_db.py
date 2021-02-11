import sqlite3
from argparse import ArgumentParser
from datetime import datetime

from django.core.management.base import BaseCommand
from tqdm import tqdm  # type: ignore
from django.contrib.postgres.search import SearchVector

from api import models


def bulk_create(model, obj_list, ignore_conflicts=True):
    model.objects.bulk_create(obj_list, ignore_conflicts=ignore_conflicts)
    return len(obj_list)


class Command(BaseCommand):
    """
    Import a magneticod sqlite3 database into dht-torznab database
    """

    help = __doc__

    def add_arguments(self, parser: ArgumentParser):
        """Add command arguments.

        Args:
            parser: argument parser
        """

        parser.add_argument(
            "database", type=str, help="Path to sqlite3 database to import"
        )

        parser.add_argument(
            "buffer-size",
            type=int,
            nargs="?",
            default=50,
            help="Buffer size when inserting torrents into dht-torznab DB",
        )

    def handle(self, *args, **options):
        """
        Creates a user with an API key if necessary and display it
        """
        conn = sqlite3.connect(
            options["database"],
        )
        conn.text_factory = bytes
        conn.row_factory = sqlite3.Row

        torrent_cursor = conn.cursor()

        torrent_cursor.execute("SELECT COUNT(*) from torrents")

        torrent_count = torrent_cursor.fetchone()[0]

        progress = tqdm(total=torrent_count)

        torrent_objs = []
        file_objs = []

        for i, torrent in enumerate(
            torrent_cursor.execute(
                "SELECT t.id, t.info_hash, t.name, t.discovered_on FROM torrents AS t;"
            )
        ):

            torrent_obj = models.Torrent(
                info_hash=torrent["info_hash"],
                name=torrent["name"].decode("utf-8", "replace"),
                discovered_on=datetime.fromtimestamp(torrent["discovered_on"]),
            )
            torrent_objs.append(torrent_obj)
            file_cursor = conn.cursor()
            for file in file_cursor.execute(
                "SELECT f.path, f.size FROM files AS f WHERE torrent_id=?",
                [str(torrent["id"])],
            ):
                file_objs.append(
                    models.File(
                        path=file["path"].decode("utf-8", "replace"),
                        size=file["size"],
                        torrent=torrent_obj,
                    )
                )

            if i % options["buffer-size"] == 0:
                bulk_create(models.Torrent, torrent_objs)
                bulk_create(models.File, file_objs)
                models.Torrent.objects.update(search_vector=SearchVector("keywords"))
                torrent_objs = []
                file_objs = []

                progress.update(options["buffer-size"])
