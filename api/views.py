from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render

from api import models


def index(request, *args, **kwargs):
    if function := request.GET.get("t", None):
        if function == "search":
            offset = int(request.GET.get("offset", "0"))
            limit = int(request.GET.get("limit", "25"))
            if query := request.GET.get("q", None):
                torrents = models.Torrent.objects.prefetch_related("files").filter(
                    name__search=query
                )
            else:
                torrents = models.Torrent.objects.prefetch_related("files").all()

            paginator = Paginator(torrents, limit)
            torrents_to_show = paginator.get_page(offset)
            return render(
                request,
                "feed.xml",
                {
                    "torrents": torrents_to_show,
                    "category": function,
                    "url": request.get_full_path(),
                    "offset": offset,
                    "total": len(torrents)
                },
                content_type="text/xml",
                status=200,
            )
        if function == "caps":
            return render(
                request,
                "caps.xml",
                {},
                content_type="text/xml",
                status=200,
            )

    return HttpResponse("test")
