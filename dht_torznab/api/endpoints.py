import pathlib
from typing import Annotated

import fastapi
from fastapi import Query, Response
from fastapi.responses import FileResponse
from lxml import etree as ET  # nosec # noqa: N812
from starlette import status

from dht_torznab import queries, schemas
from dht_torznab.api import enums, static, torznab
from dht_torznab.settings import get_settings

router = fastapi.APIRouter()


MAX_PAGE_SIZE = get_settings().API.MAX_PAGE_SIZE


# TODO build this async
def _build_xml(torrents: list[schemas.TorrentSchema], offset: int) -> bytes:
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


async def search(query: str | None, limit: int, offset: int) -> Response:
    torrent_rows = await queries.search_torrents(query, limit, offset)

    xml_bytes = _build_xml(torrent_rows, offset)
    return Response(content=xml_bytes, media_type="application/xml")


async def capabilities() -> FileResponse:
    capabilities_xml_path = pathlib.Path(*static.__path__) / "capabilities.xml"
    return FileResponse(path=capabilities_xml_path)


@router.get("")
async def torznab_endpoint(
    function: Annotated[enums.TorznabFunction, Query(alias="t")],
    query: Annotated[str | None, Query(alias="q")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[
        int,
        Query(gt=1, lte=MAX_PAGE_SIZE),
    ] = MAX_PAGE_SIZE,
) -> Response:
    match function:
        case enums.TorznabFunction.CAPS:
            return await capabilities()
        case enums.TorznabFunction.SEARCH:
            return await search(query, limit, offset)
        case _:
            raise fastapi.HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
