import factory
from faker import Factory

from api import models

faker = Factory.create()


class TorrentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Torrent

    name = faker.file_name()

    info_hash = faker.md5()

    discovered_on = faker.date_object()

    occurences = faker.pyint()

    keywords = [faker.word() for _ in range(faker.pyint(min_value=1, max_value=5))]


class FileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.File

    path = faker.file_path(faker.pyint(min_value=1, max_value=5))
    size = faker.pyint()
    torrent = factory.SubFactory(TorrentFactory)
