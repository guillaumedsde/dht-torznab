from django.db import models


class Torrent(models.Model):
    name = models.TextField()
    info_hash = models.CharField(
        # SHA1 size
        max_length=40
    )

    def __str__(self):
        return self.name


class File(models.Model):
    path = models.TextField()
    size = models.BigIntegerField()
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE, related_name="files")
