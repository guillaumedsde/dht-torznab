from rest_framework import filters, viewsets

from api import models, serializers


class TorrentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Torrent.objects.prefetch_related("files")
    serializer_class = serializers.TorrentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
