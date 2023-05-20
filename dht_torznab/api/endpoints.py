import pathlib
from collections.abc import Generator
from typing import Annotated

import fastapi
from fastapi import Query, Request, Response
from fastapi.responses import FileResponse
from lxml import etree as ET  # nosec # noqa: N812
from starlette import status
from starlette.datastructures import URL

from dht_torznab import queries, schemas
from dht_torznab.api import enums, static, torznab
from dht_torznab.settings import get_settings

router = fastapi.APIRouter()


MAX_PAGE_SIZE = get_settings().API.MAX_PAGE_SIZE


# TODO build this async
def _build_xml(
    torrents: Generator[schemas.TorrentSchema, None, None],
    offset: int,
    url: URL,
    torrent_count: int,
) -> bytes:
    xml_root_node = torznab.xml_root()
    xml_channel_node = torznab.xml_channel(
        root=xml_root_node,
        feed_url=str(url),
        # NOTE: not using .value as its type hint seems broken
        function=str(enums.TorznabFunction.SEARCH),
        offset=offset,
        total_count=torrent_count,
    )
    torznab.xml_torrents(channel=xml_channel_node, torrents=torrents)

    return ET.tostring(
        xml_root_node,
        encoding="utf-8",
        method="xml",
        xml_declaration=True,
    )


async def search(query: str | None, limit: int, offset: int, url: URL) -> Response:
    torrent_rows_generator, torrent_count = await queries.search_torrents(
        query,
        limit,
        offset,
    )

    xml_bytes = _build_xml(torrent_rows_generator, offset, url, torrent_count)
    return Response(content=xml_bytes, media_type="application/xml")


async def capabilities() -> FileResponse:
    capabilities_xml_path = pathlib.Path(*static.__path__) / "capabilities.xml"
    return FileResponse(path=capabilities_xml_path)


@router.get("")
async def torznab_endpoint(
    function: Annotated[enums.TorznabFunction, Query(alias="t")],
    request: Request,
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
            return await search(query, limit, offset, request.url)
        case _:
            raise fastapi.HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
