from rest_framework.negotiation import BaseContentNegotiation


class IgnoreClientContentNegotiation(BaseContentNegotiation):
    """ContentNegotiation class to ignore content negotiation.

    This is used because the torznab API currently only returns
    XML regardless of the client negotiation.
    """

    def select_parser(self, request, parsers):  # noqa: ANN001, ANN201
        """Select the first parser in the `.parser_classes` list."""
        return parsers[0]

    def select_renderer(
        self, request, renderers, format_suffix  # noqa: ANN001
    ):  # noqa: ANN201
        """Select the first renderer in the `.renderer_classes` list."""
        return (renderers[0], renderers[0].media_type)
