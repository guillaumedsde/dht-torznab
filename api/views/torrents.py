from rest_framework import filters, viewsets
from api.auth import TokenAuthSupportQueryString
from rest_framework.permissions import IsAuthenticated

from api import models, serializers


class TorrentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Torrent.objects.prefetch_related("files")
    serializer_class = serializers.TorrentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    authentication_classes = [TokenAuthSupportQueryString]
    permission_classes = [IsAuthenticated]
