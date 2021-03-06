# Distributed System - Search Engine

This Part and all other foo bar part of this document will be completed ASAP. Foobar is a Python library for dealing with word pluralization. feel free to contibute and ask.

## Installation

### Django Crawler & DSTea
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
$ cd [crawler_django, dstea]
$ python -m venv py_environment
$ source py_environment/bin/activate
$ pip install -r requirements.txt
$ python manage.py runserver
$ Done!!

```


### Docker-Compose
```bash
$ cd composer-docker
$ sudo docker-compose up

```

## Usage

```python
import foobar

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)

## Commands

```bash
curl -d "url=http://www.laravel.com" -X POST http://localhost:8080/crawler/crawl/
```

## Usefull Links
* https://blog.sneawo.com/blog/2017/09/07/how-to-install-pillow-psycopg-pylibmc-packages-in-pythonalpine-image/
* https://www.peterbe.com/plog/synonyms-with-elasticsearch-dsl


## Images

![empty-layout](https://github.com/Amirsorouri00/DSL-SE/blob/master/layout-empty.png)

![list-layout](https://github.com/Amirsorouri00/DSL-SE/blob/master/layout-list.png)

![dejavu-elasticsearch](https://github.com/Amirsorouri00/DSL-SE/blob/master/dejavu-elasticsearch.png)



## Usefull Links
* https://www.elastic.co/guide/en/elasticsearch/guide/master/dynamic-indices.html
* https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-analyzers.html
* http://www.devinline.com/2018/09/elasticsearch-inverted-index-and-its-storage.html
* https://gist.github.com/HonzaKral/d90d344bca18ffa71139ac11b9f83124
* https://faculty.math.illinois.edu/~riveraq2/teaching/simcamp16/PageRankwithPython.html
* https://github.com/mtusman/stock-eagle/blob/master/stockeagle/eagle.py