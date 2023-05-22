import enum


class StrEnum(str, enum.Enum):
    """StrEnum where auto() returns the field name.
    See https://docs.python.org/3.9/library/enum.html#using-automatic-values.

    Notes:
        Gotten from https://stackoverflow.com/a/74539097
    """

    @staticmethod
    def _generate_next_value_(
        name: str,
        start: int,
        count: int,
        last_values: list,
    ) -> str:
        return name.lower()


class TorznabFunction(StrEnum):
    CAPS = enum.auto()
    SEARCH = enum.auto()
    TVSEARCH = enum.auto()
    MOVIE = enum.auto()
    MUSIC = enum.auto()
    BOOK = enum.auto()
