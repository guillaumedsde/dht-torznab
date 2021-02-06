from rest_framework import serializers

from api import models


class TorrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Torrent
        fields = ["id", "name", "size", "files", "info_hash", "magneturl"]
        depth = 1
