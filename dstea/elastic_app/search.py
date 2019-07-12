__author__ = ["Amir Hossein Sorouri"]
__copyright__ = "Copyright 2019, DSL-SE"
__email__ = ["amirsorouri26@gmail.com"]
__license__ = "Apache-2.0"
__version__ = "2.0"

import os
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Search
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from . import models

# Create a connection to ElasticSearch
# hosts = "localhost"
# http_auth = ("elastic", "changeme")
# port = "9200"

hosts = [os.getenv("HOST")]
http_auth = (os.getenv("USERNAME"), os.getenv("PASSWORD"))
port = os.getenv("PORT")
connections.create_connection(hosts=hosts, http_auth=http_auth, port=port)

# ElasticSearch "model" mapping out what fields to index
class BlogPostIndex(DocType):
    author = Text()
    posted_date = Date()
    title = Text()
    text = Text()

    class Meta:
        index = 'blogpost-index'

# Bulk indexing function, run in shell
def bulk_indexing():
    BlogPostIndex.init('mypostingsx')
    es = Elasticsearch()
    bulk(client=es, actions=(b.indexing() for b in models.BlogPost.objects.all().iterator()))

# Simple search function
def search(author):
    s = Search().filter('term', author=author)
    response = s.execute()
    return response
