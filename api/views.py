from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from api import models
from rest_framework import permissions
from api import serializers

from rest_framework_xml.renderers import XMLRenderer


class RootView(APIView):
    permission_classes = [permissions.AllowAny]

    http_method_names = ["get"]
    renderer_classes = (XMLRenderer,)

    def get(self, request, format=None):
        print(request.query_params)
        if request.query_params["t"] == "search":
            torrents = self.search(request.query_params["q"])
            serialized_torrents = serializers.TorrentSerializer(torrents, many=True)
            print(type(serialized_torrents.data))
            return Response(serialized_torrents.data)

    def search(self, query_string):
        return models.Torrent.objects.filter(name__search=query_string)


class TorrentViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Torrent.objects.all()
    serializer_class = serializers.TorrentSerializer