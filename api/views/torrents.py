from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from api import models, serializers
from api.auth import TokenAuthSupportQueryString


class TorrentViewSet(viewsets.ReadOnlyModelViewSet):
    """Set of views for API torrents."""

    queryset = models.Torrent.objects.prefetch_related("files")
    serializer_class = serializers.TorrentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    authentication_classes = [TokenAuthSupportQueryString]
    permission_classes = [IsAuthenticated]
