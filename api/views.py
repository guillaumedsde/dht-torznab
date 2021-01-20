from typing import Optional, Tuple

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from api import models


def search_torrents(query: Optional[str]):
    if query:
        search_vector = SearchVector("keywords")
        search_query = SearchQuery(query, search_type="phrase")
        search_rank = SearchRank(search_vector, search_query)

        print(search_query)

        torrents = (
            models.Torrent.objects.prefetch_related("files")
            .annotate(rank=search_rank)
            .order_by("-rank")
        )
    else:
        torrents = models.Torrent.objects.prefetch_related("files").all()
    return torrents


def get_search_parameters(request: HttpRequest) -> Tuple[Optional[str], int, int]:
    query = request.GET.get("q", None)
    offset = int(request.GET.get("offset", "0")) + 1
    limit = int(request.GET.get("limit", "25"))

    # Cap limit per page
    if limit > 50:
        limit = 50

    return query, offset, limit


def search(request: HttpRequest):
    query, offset, limit = get_search_parameters(request)

    torrents = search_torrents(query)

    paginator = Paginator(torrents, limit)

    torrent_page = paginator.get_page(offset)
    print(paginator)
    print(torrent_page.object_list)
    return render(
        request,
        "feed.xml",
        {
            "torrent_page": torrent_page,
            "offset": torrent_page.number - 1,
            "category": "search",
            "url": request.get_full_path(),
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
