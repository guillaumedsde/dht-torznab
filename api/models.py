import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Torrent(BaseModel):
    name = models.TextField()
    info_hash = models.CharField(
        # SHA1 size
        max_length=40
    )
    discovered_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class File(BaseModel):
    path = models.TextField()
    size = models.BigIntegerField()
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE, related_name="files")

    def __str__(self):
        return self.path
