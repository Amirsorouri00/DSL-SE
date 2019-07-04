from django.shortcuts import render
from .explore import explore_job


def crawl(request):
    url = request.POST.get('url', None)
    explore_job(url)
    return
