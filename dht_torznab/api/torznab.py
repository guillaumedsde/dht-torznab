# safe to use lxml instead of defusedxml since we are
# generating XML, not parsing it
from collections.abc import Generator

from lxml import etree as ET  # nosec # noqa: N812

from dht_torznab import schemas
from dht_torznab.api import enums

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "torznab": "http://torznab.com/schemas/2015/feed",
}


def xml_root() -> ET._Element:
    """Generate the XML root elements for the RSS response.

    Returns:
        Root XML element
    """
    ET.register_namespace("atom", NS["atom"])
    ET.register_namespace("torznab", NS["torznab"])
    return ET.Element("rss", attrib={"version": "1.0", "encoding": "utf-8"})


def xml_channel(
    root: ET._Element,
    feed_url: str,
    function: enums.TorznabFunction,
    offset: int,
    total_count: int,
) -> ET._Element:
    """Create XML RSS channel with metadata (elements not populated).

    Args:
        root: Root XML element.
        feed_url: URL for the current feed.
        function: Current torznab function called.
        offset: Number of elements skipped.
        total_count: Total number of elements.

    Returns:
        Returns the empty RSS channel.
    """
    channel = ET.SubElement(root, "channel")

    # Link
    ET.SubElement(
        channel,
        ET.QName(NS["atom"], "link"),
        attrib={"href": feed_url, "rel": "self", "type": "application/rss+xml"},
    )

    # Title
    ET.SubElement(channel, "title").text = "torznab indexer"

    # Description
    ET.SubElement(channel, "description").text = "API results"

    # Pagination info
    ET.SubElement(
        channel,
        ET.QName(NS["torznab"], "response"),
        attrib={"offset": str(offset), "total": str(total_count)},
    ).text = function.value

    return channel


def xml_torrents(
    channel: ET._Element,
    torrents: Generator[schemas.TorrentSchema, None, None],
) -> None:
    """Add torrents to the given XML RSS channel.

    Args:
        channel: XML RSS channel.
        torrents: Generator of pydantic schemas for torrents.
    """
    for torrent in torrents:
        item = ET.SubElement(channel, "item")

        ET.SubElement(item, "title").text = torrent.name
        ET.SubElement(item, "guid", attrib={"isPermaLink": "false"}).text = str(
            torrent.id,
        )
        ET.SubElement(item, "link").text = torrent.magneturl
        ET.SubElement(item, "pubDate").text = torrent.rfc_2822_created_at
        ET.SubElement(item, "size").text = str(torrent.size)

        if torrent.peer_count is not None:
            ET.SubElement(item, "peers").text = str(torrent.peer_count)

        ET.SubElement(
            item,
            "enclosure",
            attrib={
                "url": torrent.magneturl,
                "length": str(torrent.size),
                "type": "application/x-bittorrent",
            },
        )
        ET.SubElement(
            item,
            ET.QName(NS["torznab"], "attr"),
            attrib={
                "name": "infohash",
                "value": torrent.str_info_hash,
            },
        )
        ET.SubElement(
            item,
            ET.QName(NS["torznab"], "attr"),
            attrib={
                "name": "files",
                "value": str(torrent.file_count),
            },
        )
        ET.SubElement(
            item,
            ET.QName(NS["torznab"], "attr"),
            attrib={
                "name": "magneturl",
                "value": torrent.magneturl,
            },
        )
