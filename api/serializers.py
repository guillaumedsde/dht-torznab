from rest_framework import serializers

from api import models


class TorrentSerializer(serializers.ModelSerializer):
    """Seralizer for Torrent database model."""

    info_hash = serializers.SerializerMethodField("get_str_info_hash")

    class Meta:  # noqa: D106
        model = models.Torrent
        fields = ["id", "name", "size", "files", "info_hash", "magneturl"]
        depth = 1

    def get_str_info_hash(self, obj: models.Torrent) -> str:
        """Get the Torrent infohash from the given model.

        Args:
            obj models.Torrent: the torrent object

        Returns:
            str: torrent object infohash
        """
        return obj.str_info_hash
