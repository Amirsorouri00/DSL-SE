__author__ = ["Amir Hossein Sorouri"]
__copyright__ = "Copyright 2019, DSTea"
__email__ = ["amirsorouri26@gmail.com"]
__license__ = "Apache-2.0"
__version__ = "2.0"

from django.http import HttpResponse
from django.shortcuts import render
from .explore import explore_job


def crawl(request):
    url = request.POST.get('url', None)
    res = explore_job(url)
    if 1 == res:
        return  HttpResponse(status=200)
    else:
        return HttpResponse(status=500)
