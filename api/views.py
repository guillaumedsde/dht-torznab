from typing import Optional, Tuple

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

# safe to use lxml instead of defusedxml since we are
# generating XML, not parsing it
from lxml import etree as ET  # nosec
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api import models, torznab
from api.auth import TokenAuthSupportQueryString
from api.negotiation import IgnoreClientContentNegotiation


def search_torrents(query: Optional[str]):
    if query:
        search_vector = SearchVector("keywords")
        search_query = SearchQuery(query, search_type="phrase")
        search_rank = SearchRank(search_vector, search_query)

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

    xml_root_node = torznab.xml_root()
    xml_channel_node = torznab.xml_channel(
        root=xml_root_node,
        feed_url=request.get_full_path(),
        page=torrent_page,
        function="search",
    )
    torznab.xml_torrents(channel=xml_channel_node, page=torrent_page)

    return HttpResponse(
        content=ET.tostring(
            xml_root_node, encoding="utf-8", method="xml", xml_declaration=True
        ),
        content_type="text/xml",
    )


def caps():
    return HttpResponse(open("api/static/caps.xml").read(), content_type="text/xml")


class TorznabView(APIView):
    authentication_classes = [TokenAuthSupportQueryString]
    permission_classes = [IsAuthenticated]
    content_negotiation_class = IgnoreClientContentNegotiation

    def get(self, request, format=None):
        if function := request.GET.get("t", None):
            if function == "caps":
                return caps()
            elif function == "search":
                return search(request)
            if function == "movie":
                return search(request)
        return HttpResponseBadRequest()
