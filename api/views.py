from django.http import HttpResponse
from django.shortcuts import render

from api import models


def index(request, *args, **kwargs):
    print(args)
    print(kwargs)
    if function := request.GET.get("t", None):
        if function == "search":
            if query := request.GET.get("q", None):
                torrents = models.Torrent.objects.filter(name__search=query)
                return render(
                    request,
                    "index.xml",
                    {
                        "torrents": torrents,
                        "category": function,
                        "url": request.get_full_path(),
                    },
                    content_type="text/xml",
                    status=200,
                )

    return HttpResponse("test")
