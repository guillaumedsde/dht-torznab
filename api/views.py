from rest_framework import filters, viewsets

from api import models, serializers


class TorrentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Torrent.objects.all()
    serializer_class = serializers.TorrentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
