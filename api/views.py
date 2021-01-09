from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from api import models
from rest_framework import permissions
from api import serializers


class TorrentViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Torrent.objects.all()
    serializer_class = serializers.TorrentSerializer
