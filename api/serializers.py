from django.urls import path, include
from api import models

from rest_framework import serializers, viewsets

import urllib.parse


class TorrentSerializer(serializers.ModelSerializer):

    # size of the release in bytes
    size = serializers.SerializerMethodField("get_size")

    # Number of files
    files = serializers.SerializerMethodField("get_number_files")

    # Torrent infohash
    infohash = serializers.SerializerMethodField("get_infohash")

    # Magnet uri
    magneturl = serializers.SerializerMethodField("get_magneturl")

    def get_size(self, obj):
        return sum(file.size for file in obj.files.all())

    def get_number_files(self, obj):
        return len(obj.files.all())

    def get_infohash(self, obj):
        return obj.info_hash

    def get_magneturl(self, obj):

        url_encoded_name = urllib.parse.quote(obj.name)

        return f"magnet:?xt=urn:btih:{obj.info_hash}&dn={url_encoded_name}"

    class Meta:
        model = models.Torrent
        fields = ["size", "files", "infohash", "magneturl"]