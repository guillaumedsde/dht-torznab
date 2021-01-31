from email import utils

import pytest
from faker import Factory  # type: ignore

# safe to use lxml instead of defusedxml since we are
# generating XML, not parsing it
from lxml import etree as ET  # nosec

from api import factories, torznab

faker = Factory.create()


@pytest.mark.django_db
def test_torrent_size():
    torrent = factories.TorrentFactory()
    files = factories.FileFactory.create_batch(faker.pyint(), torrent=torrent)
    assert sum(file.size for file in files) == torrent.size


@pytest.mark.django_db
def test_torrent_magneturl():
    torrent = factories.TorrentFactory(
        name="archlinux-2021.01.01-x86_64.iso",
        info_hash="944cc141baf25155bfb110273140f1e0e6687f4b",
    )

    assert (
        "magnet:?xt=urn:btih:944cc141baf25155bfb110273140f1e0e6687f4b&dn"
        "=archlinux-2021.01.01-x86_64.iso" == torrent.magneturl
    )


@pytest.mark.django_db
def test_torrent_nbr_files():
    torrent = factories.TorrentFactory()
    files = factories.FileFactory.create_batch(faker.random_int(), torrent=torrent)
    assert len(files) == torrent.nbr_files


@pytest.mark.django_db
def test_torrent_rfc_2822_discovered_on():
    dt = faker.date_time()
    torrent = factories.TorrentFactory()
    torrent.discovered_on = dt

    assert utils.format_datetime(dt) == torrent.rfc_2822_discovered_on


def test_xml_root():
    assert ET.tostring(torznab.xml_root()) == b'<rss version="1.0" encoding="utf-8"/>'
