from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from api import models


class RootView(APIView):
    def get(self, request, format=None):
        if request.query_params.t == "search":
            return self.search(request.query_params.q)

    def search(self, query_string):
        return models.Torrent.objects.filter(name__search=query_string)
