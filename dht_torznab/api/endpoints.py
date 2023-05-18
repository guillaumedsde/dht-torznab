from typing import Annotated

import fastapi
from fastapi import Query, Response
from lxml import etree as ET  # nosec # noqa: N812

from dht_torznab import models, queries
from dht_torznab.api import torznab
from dht_torznab.settings import get_settings

router = fastapi.APIRouter()


MAX_PAGE_SIZE = get_settings().API.MAX_PAGE_SIZE


# TODO build this async
def _build_xml(torrents: list[models.Torrent], offset: int) -> str:
    xml_root_node = torznab.xml_root()
    xml_channel_node = torznab.xml_channel(
        root=xml_root_node,
        feed_url="http://example.com",  # TODO
        function="search",
        offset=offset,
        total_count=1337,  # TODO
    )
    torznab.xml_torrents(channel=xml_channel_node, torrents=torrents)

    return ET.tostring(
        xml_root_node,
        encoding="utf-8",
        method="xml",
        xml_declaration=True,
    )


@router.get("")
async def torznab_endpoint(
    q: str | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[
        int,
        Query(gt=1, lte=MAX_PAGE_SIZE),
    ] = MAX_PAGE_SIZE,
) -> Response:
    torrents = await queries.search_torrents(q, limit, offset)

    xml_string = _build_xml(torrents, offset)
    return Response(content=xml_string, media_type="application/xml")
