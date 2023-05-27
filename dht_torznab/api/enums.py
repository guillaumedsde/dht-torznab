import enum
from typing import Any


class StrEnum(str, enum.Enum):
    """StrEnum where auto() returns the field name.

    Notes:
        See https://docs.python.org/3.9/library/enum.html#using-automatic-values.
        Gotten from https://stackoverflow.com/a/74539097.
    """

    @staticmethod
    def _generate_next_value_(
        name: str,
        # NOTE: following parameters are required by method signature
        start: int,  # noqa: ARG004
        count: int,  # noqa: ARG004
        last_values: list[Any],  # noqa: ARG004
    ) -> str:
        return name.lower()


class TorznabFunction(StrEnum):
    CAPS = enum.auto()
    SEARCH = enum.auto()
    TVSEARCH = enum.auto()
    MOVIE = enum.auto()
    MUSIC = enum.auto()
    BOOK = enum.auto()
