from typing import Optional, Tuple

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from api import models


def search_torrents(query: Optional[str]):
    if query:
        torrents = (
            models.Torrent.objects.prefetch_related("files")
            .filter(name__search=query, files__path__search=query)
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
        if function == "search":
            return search(request)
        elif function == "caps":
            return caps(request)

    return HttpResponse("test")
