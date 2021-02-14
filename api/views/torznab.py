from typing import Optional, Tuple

from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

# safe to use lxml instead of defusedxml since we are
# generating XML, not parsing it
from lxml import etree as ET  # nosec # noqa: N812
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from api import models, torznab
from api.auth import TokenAuthSupportQueryString
from api.negotiation import IgnoreClientContentNegotiation


def search_torrents(query: Optional[str]) -> QuerySet[models.Torrent]:
    """Search torrents optionally with given query.

    Args:
        query (Optional[str]): Torrent search query.

    Returns:
        QuerySet[models.Torrent]: Torrent queryset.
    """
    if query:
        search_vector = SearchVector("keywords")
        search_query = SearchQuery(query, search_type="phrase")
        search_rank = SearchRank(search_vector, search_query)

        torrents = (  # noqa: ECE001
            models.Torrent.objects.prefetch_related("files")
            .annotate(rank=search_rank)
            .order_by("-rank")
        )
    else:
        torrents = models.Torrent.objects.prefetch_related("files").all()
    return torrents


def get_search_parameters(request: HttpRequest) -> Tuple[Optional[str], int, int]:
    """Extract search parameters from an HttpRequest for searching torrents.

    Fall back to  default values when the parameters are not found

    Args:
        request (HttpRequest): HttpRequest for searching torrents

    Returns:
        Tuple[Optional[str], int, int]: query, offset and limit search parameters
    """
    query = request.GET.get("q", None)
    offset = int(request.GET.get("offset", "0")) + 1
    limit = int(request.GET.get("limit", settings.PAGE_SIZE))

    # Cap limit per page
    if limit > settings.PAGE_SIZE:
        limit = settings.PAGE_SIZE

    return query, offset, limit


def search(request: HttpRequest) -> HttpResponse:
    """Search for torrents given an HttpRequest.

    Return a Torznab XML response with the search results

    Args:
        request (HttpRequest): HttpRequest for torrent search

    Returns:
        HttpResponse: XML response with the search results
    """
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
            xml_root_node,
            encoding="utf-8",
            method="xml",
            xml_declaration=True,
        ),
        content_type="text/xml",
    )


def caps() -> HttpResponse:
    """Torznab view returning this indexer's capabilities.

    Returns:
        HttpResponse: the Torznab HTTP response
    """
    with open("api/static/caps.xml") as caps_xml:
        return HttpResponse(caps_xml.read(), content_type="text/xml")


class TorznabView(APIView):
    """The Torznab API view."""

    authentication_classes = [TokenAuthSupportQueryString]
    permission_classes = [IsAuthenticated]
    content_negotiation_class = IgnoreClientContentNegotiation  # type: ignore

    def get(self, request: Request) -> HttpResponse:
        """Handle HTTP GET Request by rendering an XML Torznab response.

        Args:
            request (Request): The HTTP GET Request

        Returns:
            HttpResponse: Generated response
        """
        if function := request.GET.get("t", None):
            if function == "caps":
                return caps()
            elif function == "search":
                return search(request)
            if function == "movie":
                return search(request)
        return HttpResponseBadRequest()
