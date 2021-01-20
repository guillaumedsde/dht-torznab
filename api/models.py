import urllib.parse
import uuid
from email import utils

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Torrent(BaseModel):
    name = models.TextField()
    info_hash = models.CharField(
        # SHA1 size
        max_length=40
    )
    discovered_on = models.DateTimeField(auto_now_add=True)
    keywords = models.TextField()

    search_vector = SearchVectorField(null=True)

    @property
    def size(self):
        return sum(file.size for file in self.files.all())

    @property
    def magneturl(self):

        url_encoded_name = urllib.parse.quote(self.name)

        return f"magnet:?xt=urn:btih:{self.info_hash}&dn={url_encoded_name}"

    @property
    def nbr_files(self):
        return len(self.files.all())

    @property
    def rfc_2822_discovered_on(self):
        return utils.format_datetime(self.discovered_on)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-discovered_on"]
        constraints = [
            models.UniqueConstraint(
                fields=["info_hash", "name"], name="unique-name-info_hash"
            )
        ]
        indexes = [GinIndex(fields=["search_vector"])]


class File(BaseModel):
    path = models.TextField()
    size = models.BigIntegerField()
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE, related_name="files")

    def __str__(self):
        return self.path

    class Meta:
        ordering = ["-path"]
