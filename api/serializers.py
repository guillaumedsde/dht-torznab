from rest_framework import serializers

from api import models


class TorrentSerializer(serializers.ModelSerializer):

    info_hash = serializers.SerializerMethodField("get_str_info_hash")

    class Meta:
        model = models.Torrent
        fields = ["id", "name", "size", "files", "info_hash", "magneturl"]
        depth = 1

    def get_str_info_hash(self, obj):
        return obj.str_info_hash
