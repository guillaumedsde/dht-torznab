from django.db import models
import uuid


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class Torrent(BaseModel):
    name = models.TextField()
    info_hash = models.CharField(
        # SHA1 size
        max_length=40
    )
    discovered_on = models.DateTimeField(auto_now_add=True)


class File(BaseModel):
    path = models.TextField()
    size = models.BigIntegerField()
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE, related_name="files")
