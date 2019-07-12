__author__ = ["Amir Hossein Sorouri"]
__copyright__ = "Copyright 2019, DSL-SE"
__email__ = ["amirsorouri26@gmail.com"]
__license__ = "Apache-2.0"
__version__ = "2.0"

from . import url
from datetime import datetime
from elasticsearch_dsl import Document, Date, token_filter \
        , DateRange, Keyword, Text, Object, analyzer



synonym_tokenfilter = token_filter(
    'synonym_tokenfilter',
    'synonym',
    synonyms=[
        'reactjs, react',  # <-- important
    ],
)

text_analyzer = analyzer(
    'text_analyzer',
    tokenizer='standard',
    filter=[
        # The ORDER is important here.
        'standard',
        'lowercase',
        'stop',
        synonym_tokenfilter,
        # Note! 'snowball' comes after 'synonym_tokenfilter'
        'snowball',
    ],
    char_filter=['html_strip']
)


class Web(Document):
    url = Keyword()
    domain = Keyword()
    homepage = Text()
    created_date = Date()
    last_updated = Date()

    def save(self, **kwargs):
        if not self.created_date:
            self.created_date = datetime.now()
        self.last_updated = datetime.now()
        
        return super(Web, self).save('default', 'web', True, **kwargs)

    def set_name(self):
        return Web.Index('web')    

class WebPage(Document):
    url = Keyword()
    title = Text(analyzer=text_analyzer)
    description = Text(
        fields={'raw': Keyword()},
        analyzer=text_analyzer
    )
    body = Text(
        fields={'raw': Keyword()},
        analyzer=text_analyzer
    )
    web = Object()
    weight = Keyword()

    def save(self, **kwargs):
        # self.set_name()
        lang = url.detect_language(self.body)
        return super(WebPage, self).save('default', 'page-%s'%lang, True, **kwargs)