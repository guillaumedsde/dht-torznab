# safe to use lxml instead of defusedxml since we are
# generating XML, not parsing it
from lxml import etree as ET  # nosec # noqa: N812

from dht_torznab import schemas

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "torznab": "http://torznab.com/schemas/2015/feed",
}


def xml_root() -> ET._Element:
    """Generate the XML root elements for the RSS response.

    Returns:
    -------
        ET._Element: Root XML elements
    """
    ET.register_namespace("atom", NS["atom"])
    ET.register_namespace("torznab", NS["torznab"])
    return ET.Element("rss", attrib={"version": "1.0", "encoding": "utf-8"})


def xml_channel(
    root: ET._Element,
    feed_url: str,
    function: str,
    offset: int,
    total_count: int,
) -> ET._Element:
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

    # Category
    ET.SubElement(channel, "category").text = function

    # Pagination info
    ET.SubElement(
        channel,
        ET.QName(NS["torznab"], "response"),
        attrib={"offset": str(offset), "total": str(total_count)},
    ).text = function

    return channel


def xml_torrents(channel: ET._Element, torrents: list[schemas.TorrentSchema]) -> None:
    for torrent in torrents:
        item = ET.SubElement(channel, "item")

        ET.SubElement(item, "title").text = torrent.name
        ET.SubElement(item, "guid", attrib={"isPermaLink": "false"}).text = str(
            torrent.id,
        )
        ET.SubElement(item, "link").text = torrent.magneturl
        ET.SubElement(item, "pubDate").text = torrent.rfc_2822_created_at
        ET.SubElement(item, "size").text = str(torrent.size)

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
