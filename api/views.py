import operator
import re
from functools import reduce
from typing import Optional, Tuple

from django.contrib.postgres import search
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from api import models


def search_torrents(query: Optional[str]):
    if query:
        # tokenize query
        search_query = [
            Q(name__icontains=term) for term in re.split(r"(?u)\b\w\w+\b", query)
        ]
        torrents = (
            models.Torrent.objects.prefetch_related("files")
            .filter(reduce(operator.or_, search_query))
            .distinct()
        )
    else:
        torrents = models.Torrent.objects.prefetch_related("files").all()
    return torrents


def get_search_parameters(request: HttpRequest) -> Tuple[Optional[str], int, int]:
    query = request.GET.get("q", None)
    offset = int(request.GET.get("offset", "0"))
    limit = int(request.GET.get("limit", "25"))

    # Cap limit per page
    if limit > 50:
        limit = 50

    print(query)

    return query, offset, limit


def search(request: HttpRequest):
    query, offset, limit = get_search_parameters(request)

    torrents = search_torrents(query)

    paginator = Paginator(torrents, limit)
    torrents_to_show = paginator.get_page(offset)
    return render(
        request,
        "feed.xml",
        {
            "torrents": torrents_to_show,
            "category": "search",
            "url": request.get_full_path(),
            "offset": offset,
            "total": len(torrents),
        },
        content_type="text/xml",
        status=200,
    )


def caps(request: HttpRequest):
    return render(
        request,
        "caps.xml",
        {},
        content_type="text/xml",
        status=200,
    )


def index(request: HttpRequest, *args, **kwargs):
    if function := request.GET.get("t", None):
        if function == "caps":
            return caps(request)
        elif function == "search":
            return search(request)
        if function == "movie":
            return search(request)

    return HttpResponse("test")
