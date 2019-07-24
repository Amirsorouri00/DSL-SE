__author__ = ["Amir Hossein Sorouri", "Anthony Sigogne"]
__copyright__ = "Copyright 2019, DSL-SE"
__email__ = ["amirsorouri26@gmail.com", "anthony@byprog.com"]
__license__ = "Apache-2.0"
__version__ = "2.0"

import os
import json
from . import re
from . import query
from django.http import JsonResponse
from django.http import HttpResponse
from elasticsearch.helpers import bulk
import elastic_app.analyzer as analyzer
from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.query import Q
from elasticsearch_dsl import DocType, Text, Date, Search

# Create a connection to ElasticSearch
# hosts = "localhost"
# http_auth = ("elastic", "changeme")
# port = "9200"

hosts = [os.getenv("HOST")]
http_auth = (os.getenv("USERNAME"), os.getenv("PASSWORD"))
port = os.getenv("PORT")
client = connections.create_connection(hosts=hosts, http_auth=http_auth, port=port)

def search(inputs):
    """
    URL : /search
    Query engine to find a list of relevant URLs.
    Method : POST
    Form data :
        - query : the search query [string, required]
        - hits : the number of hits returned by query [integer, optional, default:10]
        - start : the start of hits [integer, optional, default:0]
    Return a sublist of matching URLs sorted by relevance, and the total of matching URLs.
    """
    def format_result(hit, highlight) :
        # highlight title and description
        title = hit["title"]
        description = hit["description"]
        if highlight :
            if "description" in highlight :
                description = highlight["description"][0]+"..."
            elif "body" in highlight :
                description = highlight["body"][0]+"..."
            """if "title" in highlight :
                title = highlight["title"][0]"""

        # create false title and description for better user experience
        if not title :
            title = hit["domain"]
        if not description :
            description = analyzer.create_description(hit["body"])+"..."

        return {
            "title":title,
            "description":description,
            "url":hit["url"],
            "thumbnail":hit.get("thumbnail", None)
        }

    # get POST data
    data = dict((key, inputs.get(key)) for key in inputs)
    if "query" not in data :
        raise InvalidUsage('No query specified in POST data')
    start = int(data.get("start", "0"))
    hits = int(data.get("hits", "30"))
    if start < 0 or hits < 0 :
        raise InvalidUsage('Start or hits cannot be negative numbers')

    # analyze user query
    groups = re.search("(site:(?P<domain>[^ ]+))?( ?(?P<query>.*))?",data["query"]).groupdict()
    
    if groups.get("query", False) and groups.get("domain", False) :
        # expression in domain query
        response = client.search(index="page*", body=query.domain_expression_query(groups["domain"], groups["query"]), from_=start, size=hits)
        results = [format_result(hit["_source"], hit.get("highlight", None)) for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]

    elif groups.get("domain", False) :
        # domain query
        response = client.search(index="page*", body=query.domain_query(groups["domain"]), from_=start, size=hits)
        results = [format_result(hit["_source"], None) for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]

    elif groups.get("query", False) :
        response = client.search(index="page*", body=query.expression_query(groups["query"]))
        results = []
        for domain_bucket in response['aggregations']['per_domain']['buckets']:
            for hit in domain_bucket["top_results"]["hits"]["hits"] :
                results.append((format_result(hit["_source"], hit.get("highlight", None)),hit["_score"]))
        results = [result[0] for result in sorted(results, key=lambda result: result[1], reverse=True)]
        total = len(results)
        results = results[start:start+hits]
    return json.dumps(dict(total=total, results=results))

import attrdict

def as_attrdict(val):
    if not isinstance(val, attrdict.AttrDict):
        print(val)
        raise TypeError('not AttrDict')
    return dict(val)

def another_search(inputs):
    """
    URL : /search
    Query engine to find a list of relevant URLs.
    Method : POST
    Form data :
        - query : the search query [string, required]
        - hits : the number of hits returned by query [integer, optional, default:10]
        - start : the start of hits [integer, optional, default:0]
        - highlight : return highlight parts for each URL [integer, optional, default:0]
    Return a sublist of matching URLs sorted by relevance, and the total of matching URLs.
    """
    # get POST data
    data = dict((key, inputs.get(key)) for key in inputs)
    if "query" not in data :
        raise InvalidUsage('No query specified in POST data')
    start = int(data.get("start", "0"))
    hits = int(data.get("hits", "30"))
    if start < 0 or hits < 0 :
        raise InvalidUsage('Start or hits cannot be negative numbers')
    highlight = int(data.get("highlight", "0"))

    # query search engine
    s = Search(index="page-*").using(client).highlight('title', 'description', pre_tags="<b>", post_tags="</b>")
    q = Q("multi_match", query=data["query"], fields=['title', 'description', 'body'])
    s = s.query(q)[start:start+hits]

    # return list of matching results
    results = [{
        "url":hit.url,
        "title":hit.meta.highlight.title[0] if highlight and "highlight" in hit.meta and "title" in hit.meta.highlight else hit.title,
        "description":hit.meta.highlight.description[0] if highlight and "highlight" in hit.meta and "description" in hit.meta.highlight else hit.description
        } for hit in s]
    total = len(results)
    # raise InvalidUsage(str(results))
    return json.dumps(dict(total=total, results=results))
    # return jsonify(total=s.count(), results=[{
    #     "url":hit.url,
    #     "title":hit.meta.highlight.title[0] if highlight and "highlight" in hit.meta and "title" in hit.meta.highlight else hit.title,
    #     "description":hit.meta.highlight.description[0] if highlight and "highlight" in hit.meta and "description" in hit.meta.highlight else hit.description
    #     } for hit in s])