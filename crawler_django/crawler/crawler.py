__author__ = ["Amir Hossein Sorouri", "Anthony Sigogne"]
__copyright__ = "Copyright 2019, DSL-SE"
__email__ = ["amirsorouri26@gmail.com", "anthony@byprog.com"]
__license__ = "Apache-2.0"
__version__ = "2.0"

import datetime
import requests
from .elastic_index_class import Web, WebPage, InvertedIndex
import os
from . import url
import scrapy
import base64
import io
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from elasticsearch_dsl import Document, DateRange, Keyword, Range, Text, Object
from .language import languages
from collections import Counter
from PIL import Image
from rq.decorators import job
from rq import Queue
from elasticsearch_dsl.connections import connections

# Create a connection to ElasticSearch
# hosts = "localhost"
# http_auth = ("elastic", "changeme")
# port = "9200"

hosts = [os.getenv("HOST")]
http_auth = (os.getenv("USERNAME"), os.getenv("PASSWORD"))
port = os.getenv("PORT")
client = connections.create_connection(hosts=hosts, http_auth=http_auth, port=port)


class Crawler(scrapy.spiders.CrawlSpider):
    """
    Explore a website and index all urls.
    """
    name = 'crawler'
    handle_httpstatus_list = [301, 302, 303] # redirection allowed
    rules = (
        # Extract all inner domain links with state "follow"
        Rule(LinkExtractor(), callback='parse_items', follow=True, process_links='links_processor'),
    )
    
    web = None    
    es_client=None  # elastic client
    redis_conn=None # redis client

    def links_processor(self,links):
        """
        A hook into the links processing from an existing page, done in order to not follow "nofollow" links
        """
        ret_links = list()
        if links:
            for link in links:
                if not link.nofollow:
                    ret_links.append(link)
        return ret_links

    def parse_items(self, response):
        """
        Parse and analyze one url of website.
        """
        yield pipeline(response, self)

def pipeline(response, spider):
    """
    Index a page.
    """
    # skip rss or atom urls
    if not response.css("html").extract_first() :
        return

    # get domain
    domain = url.domain(response.url)

    # extract title
    title = response.css('title::text').extract_first()
    title = title.strip() if title else ""

    # get main language of page, and main content of page
    lang = url.detect_language(response.body)
    if lang not in languages :
        raise InvalidUsage('Language not supported')
    body, boilerplate = url.extract_content(response.body, languages.get(lang))

        # extract description
    description = response.css("meta[name=description]::attr(content)").extract_first()
    if description:
        description = description.strip() if description else ""
    else:
        description = url.create_description(body)
        description = description.strip() if description else ""
    

    # weight of page
    weight = 3
    if not title and not description :
        weight = 0
    elif not title :
        weight = 1
    elif not description :
        weight = 2
    if body.count(" ") < boilerplate.count(" ") or not url.create_description(body) :
        # probably bad content quality
        weight -= 1
        
    # WebPage.init()
    first = WebPage(url=response.url, title=title, domain=domain \
                    , description=description, body=body, web=spider.web, weight=weight)
    first.save()


    # invin = url.create_inverted_index("%s.%s"%(body,description))
    # for word in sorted(invin.keys()):
    #     invIndex = InvertedIndex(word = word, url = response.url, weight = invin[word])
    #     invIndex.save()

    # try to create thumbnail from page
    img_link = response.css("meta[property='og:image']::attr(content)").extract_first()
    if not img_link :
        img_link = response.css("meta[name='twitter:image']::attr(content)").extract_first()
    if img_link :
        q = Queue(connection=spider.redis_conn)
        q.enqueue(create_thumbnail, response.url, lang, img_link)

    # check for redirect url
    if response.status in spider.handle_httpstatus_list and 'Location' in response.headers:
        newurl = response.headers['Location']
        meta = {'dont_redirect': True, "handle_httpstatus_list" : spider.handle_httpstatus_list}
        meta.update(response.request.meta)
        return Request(url = newurl.decode("utf8"), meta = meta, callback=spider.parse)


def create_thumbnail(url_id, lang, link) :
    """
    Create a thumbnail from image link.
    """
    print("create thumbnail of : %s"%link)

    size = 143, 143
    r = requests.get(link, stream=True) # get image data
    if r.status_code == 200:
        img = Image.open(io.BytesIO(r.content))
        format_ = img.format # format of image (mime type: jpg, png,...)
        longer_side = max(img.size)
        horizontal_padding = (longer_side - img.size[0]) / 2
        vertical_padding = (longer_side - img.size[1]) / 2
        # crop image
        img = img.crop(
            (
                -horizontal_padding,
                -vertical_padding,
                img.size[0] + horizontal_padding,
                img.size[1] + vertical_padding
            )
        )
        img.thumbnail(size) # create thumbnail
        # encode in base64
        buffer_ = io.BytesIO()
        img.save(buffer_, format=format_)
        img_str = b"data:image/%s;base64,%s"%(format_.lower().encode("utf8"),base64.b64encode(buffer_.getvalue()))
        img_str = img_str.decode("utf8")

        # finally, save into elasticsearch
        url = client.get(index="web-%s"%lang, doc_type='page', id=url_id)
        url["_source"]["thumbnail"] = img_str
        res = client.index(index="web-%s"%lang, doc_type='page', id=url_id, body=url["_source"])
        return 1

    return 0
