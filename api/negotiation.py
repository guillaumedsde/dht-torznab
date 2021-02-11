from rest_framework.negotiation import BaseContentNegotiation


class IgnoreClientContentNegotiation(BaseContentNegotiation):
    def select_parser(self, request, parsers):  # noqa: ANN001
        """Select the first parser in the `.parser_classes` list."""
        return parsers[0]

    def select_renderer(self, request, renderers, format_suffix):  # noqa: ANN001
        """Select the first renderer in the `.renderer_classes` list."""
        return (renderers[0], renderers[0].media_type)
