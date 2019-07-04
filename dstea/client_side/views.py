from django.shortcuts import render
from django.http import HttpResponse
import json


def ui_one(request, format=None):
    context = {"here": "here"}
    return render(request, 'client_side/layout.html', context)
    # return JsonResponse({'received data': request.POST}, safe=False, status=200)

def ui_two(request, format=None):
    context = {"here": "here"}
    return render(request, 'client_side/layout-empty.html', context)


# import requests
# host = "127.0.0.1"
# port = "5000"
def search(request, format=None):
    """
    URL : /
    Query engine to find a list of relevant URLs.
    Method : POST or GET (no query)
    Form data :
        - query : the search query
        - hits : the number of hits returned by query
        - start : the start of hits
    Return a template view with the list of relevant URLs.
    """
    # GET data
    query = request.GET.get("query", None)
    start = request.GET.get("start", 0)
    hits = request.GET.get("hits", 10)
    if start < 0 or hits < 0 :
        return "Error, start or hits cannot be negative numbers"

    if query :
        # query search engine
        try :
            # r = requests.post('http://%s:%s/search'%(host, port), data = {
            #     'query':query,
            #     'hits':hits,
            #     'start':start,
            #     'highlight':1
            # })
            data = {
                'query':query,
                'hits':hits,
                'start':start,
                'highlight':1
            }
            print('here')
            from elastic_app.search_engine import search
            import time
            start = time.time()
            r = search(data)
            end = time.time()
        except Exception as e:
            return HttpResponse('%s (%s)' % (e, type(e)))

        # get data and compute range of results pages
        data = json.loads(r)
        # data = r
        i = int(start/hits)
        range_pages = range(i-5,i+5) if i >= 6 else range(0,1+int(data["total"]/hits))

        # show the list of matching results
        return render(request, 'client_side/layout.html', {
            "query": query,
            "response_time": end - start,
            "total": data["total"],
            "hits": hits,
            "start": start,
            "range_pages": range_pages,
            "results": data["results"]    
        })

    # return homepage (no query)
    return render(request, 'client_side/layout-empty.html')
