
__author__ = ["Amir Hossein Sorouri", "Anthony Sigogne"]
__copyright__ = "Copyright 2019, DSTea"
__email__ = ["amirsorouri26@gmail.com", "anthony@byprog.com"]
__license__ = "GNU"
__version__ = "1.0"


# import url
import os
import crawler
import requests
import tldextract
from redis import Redis
from datetime import datetime
from rq.decorators import job
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from elasticsearch_dsl import Index, Search, Mapping
from elasticsearch_dsl.connections import connections

# initiate the elasticsearch connection

hosts = [os.getenv("HOST")]
http_auth = (os.getenv("USERNAME"), os.getenv("PASSWORD"))
port = os.getenv("PORT")
# hosts = "localhost"
# http_auth = ("elastic", "changeme")
# port = "9200"
client = connections.create_connection(hosts=hosts, http_auth=http_auth, port=port)

# initiate Redis connection

# redis_conn = Redis(os.getenv("REDIS_HOST", "redis"), os.getenv("REDIS_PORT", 6379))
redis_conn = Redis("127.0.0.1", os.getenv("REDIS_PORT", 6379))


def domains(url) :
    """
    Get the domain of the url.
    """
    return tldextract.extract(url).registered_domain

def crawl(url) :
    """
    Crawl an URL.
    Return URL data.
    """
    try :
        r = requests.get(url)
    except :
        return None
    return r

# @app.route("/explore", methods=['POST'])
def explore():
    """
    URL : /explore
    Explore a website and index all urls
    Method : POST
    Form data :
        - url : the url to explore [string, required]
    Return a success message (means redis-rq process launched).
    """
    # get POST data
    data = dict((key, request.form.get(key)) for key in request.form.keys())
    if "url" not in data :
        raise InvalidUsage('No url specified in POST data')

    # launch exploration job
    explore_job.delay(data["url"])

    return "Exploration started"

@job('default', connection=redis_conn)
def explore_job(link) :
    """
    Explore a website and index all urls (redis-rq process).
    """
    print("explore website at : %s"%link)

    # get final url after possible redictions
    try :
        link = crawl(link).url
        print
    except :
        return 0

    # create or update domain data
    domain = domains(link)
    res = client.index(index="web", doc_type='domain', id=domain, body={
        "homepage":link,
        "domain":domain,
        "last_crawl":datetime.now()
    })

    # start crawler
    process = CrawlerProcess({
        'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
        'DOWNLOAD_TIMEOUT':100,
        'DOWNLOAD_DELAY':0.45,
        'ROBOTSTXT_OBEY':True,
        'HTTPCACHE_ENABLED':False,
        'REDIRECT_ENABLED':False,
        'SPIDER_MIDDLEWARES' : {
            'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware':True,
            'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware':True,
            'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware':True,
            'scrapy.extensions.closespider.CloseSpider':True
        },
        'CLOSESPIDER_PAGECOUNT':500 #only for debug
    })
    process.crawl(crawler.Crawler, allowed_domains=[urlparse(link).netloc], start_urls = [link,], es_client=client, redis_conn=redis_conn)
    process.start()

    return 1