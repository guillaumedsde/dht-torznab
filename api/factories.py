import factory  # type: ignore
from faker import Factory  # type: ignore

from api import models

fake = Factory.create()


class TorrentFactory(factory.django.DjangoModelFactory):
    """Create a fake Torrent object."""

    class Meta:  # noqa: D106
        model = models.Torrent

    name = fake.file_name()

    info_hash = fake.binary(length=128)

    discovered_on = fake.date_object()

    occurences = fake.pyint()

    keywords = [fake.word() for _ in range(fake.pyint(min_value=1, max_value=5))]


class FileFactory(factory.django.DjangoModelFactory):
    """Create a fake File object with a fake Torrent."""

    class Meta:  # noqa: D106
        model = models.File

    path = fake.file_path(fake.pyint(min_value=1, max_value=5))
    size = fake.pyint()
    torrent = factory.SubFactory(TorrentFactory)
