import urllib.parse

from rest_framework import serializers

from api import models


class TorrentSerializer(serializers.ModelSerializer):

    # size of the release in bytes
    size = serializers.SerializerMethodField("get_size")

    # Magnet uri
    magneturl = serializers.SerializerMethodField("get_magneturl")

    def get_size(self, obj):
        return sum(file.size for file in obj.files.all())

    def get_magneturl(self, obj):

        url_encoded_name = urllib.parse.quote(obj.name)

        return f"magnet:?xt=urn:btih:{obj.info_hash}&dn={url_encoded_name}"

    class Meta:
        model = models.Torrent
        fields = ["id", "name", "size", "files", "info_hash", "magneturl"]
        depth = 1
