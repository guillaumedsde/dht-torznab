import binascii
from datetime import datetime
from email import utils
from urllib import parse

import pydantic


class TorrentSchema(pydantic.BaseModel):
    id: int = pydantic.Field(..., ge=0)
    name: str
    created_at: datetime
    info_hash: bytes
    file_count: int = pydantic.Field(..., gt=0)
    size: int = pydantic.Field(..., ge=0)

    @property
    def str_info_hash(self) -> str:
        """Compute a string representation of the binary torrent info hash.

        Returns:
        -------
            str: torrent infohash
        """
        return binascii.b2a_hex(self.info_hash).decode("utf-8")

    @property
    def magneturl(self) -> str:
        """Build the torrent magnet URL.

        Returns:
        -------
            str: torrent magnet URL
        """
        url_encoded_name = parse.quote(self.name)

        return f"magnet:?xt=urn:btih:{self.str_info_hash}&dn={url_encoded_name}"

    @property
    def rfc_2822_created_at(self) -> str:
        """Compute the torrent's discovery date as an RFC2822 formatted date.

        Returns:
            str: RFC2822 formatted discovery date
        """
        return utils.format_datetime(self.created_at)
