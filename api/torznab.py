from django.core.paginator import Page

# safe to use lxml instead of defusedxml since we are
# generating XML, not parsing it
from lxml import etree as ET  # nosec

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "torznab": "http://torznab.com/schemas/2015/feed",
}


def xml_root() -> ET._Element:
    ET.register_namespace("atom", NS["atom"])
    ET.register_namespace("torznab", NS["torznab"])
    root = ET.Element("rss", attrib={"version": "1.0", "encoding": "utf-8"})
    return root


def xml_channel(
    root: ET._Element, feed_url: str, function: str, page: Page
) -> ET._Element:
    channel = ET.SubElement(root, "channel")

    # Link
    ET.SubElement(
        channel,
        ET.QName(NS["atom"], "link"),  # type: ignore
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
        ET.QName(NS["torznab"], "response"),  # type: ignore
        attrib={"offset": str(page.number), "total": str(page.paginator.count)},
    ).text = function

    return channel


def xml_torrents(channel: ET._Element, page: Page):
    for torrent in page.object_list:
        item = ET.SubElement(channel, "item")

        ET.SubElement(item, "title").text = torrent.name
        ET.SubElement(item, "guid", attrib={"isPermaLink": "false"}).text = str(
            torrent.id
        )
        ET.SubElement(item, "link").text = torrent.magneturl
        ET.SubElement(item, "pubDate").text = torrent.rfc_2822_discovered_on
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
            ET.QName(NS["torznab"], "attr"),  # type: ignore
            attrib={
                "name": "size",
                "value": str(torrent.size),
            },
        )
        ET.SubElement(
            item,
            ET.QName(NS["torznab"], "attr"),  # type: ignore
            attrib={
                "name": "infohash",
                "value": torrent.info_hash,
            },
        )
        ET.SubElement(
            item,
            ET.QName(NS["torznab"], "attr"),  # type: ignore
            attrib={
                "name": "files",
                "value": str(torrent.nbr_files),
            },
        )
        ET.SubElement(
            item,
            ET.QName(NS["torznab"], "attr"),  # type: ignore
            attrib={
                "name": "magneturl",
                "value": torrent.magneturl,
            },
        )
