from urllib import parse
import uuid
from email import utils

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class BaseModel(models.Model):
    """Base abstract model used as base for all models."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:  # noqa: WPS306, D106
        abstract = True


class Torrent(BaseModel):
    """Django ORM model for Torrent."""

    name = models.TextField()
    info_hash = models.CharField(
        # SHA1 size
        max_length=40  # noqa: WPS432
    )
    discovered_on = models.DateTimeField(
        auto_now_add=True, help_text="Date on which this torrent was discovered"
    )
    occurences = models.PositiveIntegerField(
        default=1,
        help_text="Count of occurences of this particular torrent",
    )
    keywords = models.TextField(
        help_text="Keywords extracted from torrent name to help with search"
    )

    search_vector = SearchVectorField(null=True)

    @property
    def size(self):
        return sum(torrent_file.size for torrent_file in self.files.all())

    @property
    def magneturl(self):

        url_encoded_name = parse.quote(self.name)

        return f"magnet:?xt=urn:btih:{self.info_hash}&dn={url_encoded_name}"

    @property
    def nbr_files(self):
        return len(self.files.all())

    @property
    def rfc_2822_discovered_on(self):
        return utils.format_datetime(self.discovered_on)

    def __str__(self):  # pragma: no cover
        return self.name

    class Meta:  # noqa: WPS306, D106
        ordering = ["-discovered_on"]
        constraints = [
            models.UniqueConstraint(
                fields=["info_hash", "name"], name="unique-name-info_hash"
            )
        ]
        indexes = [GinIndex(fields=["search_vector"])]


class File(BaseModel):
    """Django ORM model for a Torrent file object."""

    path = models.TextField()
    size = models.BigIntegerField()
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE, related_name="files")

    def __str__(self):  # pragma: no cover
        return self.path

    class Meta:  # noqa: WPS306, D106
        ordering = ["-path"]
