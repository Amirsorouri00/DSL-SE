from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Search
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from . import models

# Create a connection to ElasticSearch
hosts = "localhost"
http_auth = ("elastic", "changeme")
# http_auth = (os.getenv("USERNAME"), os.getenv("PASSWORD"))
# port = os.getenv("PORT")
port = "9200"
connections.create_connection(hosts=hosts, http_auth=http_auth, port=port)
# connections.create_connection()

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