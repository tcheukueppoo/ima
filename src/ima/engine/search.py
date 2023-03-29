#!/usr/bin/env python

import re, requests

from urllib3.util import parse_url
from bs4          import BeautifulSoup
from .utils       import goto

class Search:
    search_urls = {
        'duckduckgo': 'duckduckgo.com/html/?q={0}',
        'google'    : 'www.google.com/search?q={0}',
        'yahoo'     : 'search.yahoo.com/search/?p={0}'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'
    }

    @staticmethod
    def check_engine(engine):
        if not engine in Search.search_urls.keys():
            raise Exception('search engine <' + engine + '> is unsupported')

    @staticmethod
    def get_url(engine, query):
        return 'https://' + Search.search_urls[engine].format(query.replace(' ', '+'))

    def __init__(self, **kargs):
        self.page    = ''
        self.query   = kargs.get('query', '')
        self.engine  = kargs.get('engine', 'google')
        self.index   = kargs.get('index', 1)
        self.session = requests.Session()
        Search.check_engine(self.engine)
        self.url = Search.get_url(self.engine, self.query)

    def set_query(self, query):
        self.query = query
        self.url = Search.get_url(self.engine, self.query)
        return self

    def set_engine(self, engine):
        Search.check_engine(engine)
        self.engine = engine
        self.url    = Search.get_url(self.engine, self.query)
        return self

    def set_url(self, url):
        self.url = url
        return self

    def _decode_url(self, url):
        def replace(match):
            return bytearray.fromhex(match.group(1)).decode()
        return re.sub(r'%([a-fA-F0-9]{2})', replace, url)

    def _extract_links(self):
        urls        = []
        query_regex = {
            'google'    : re.compile('imgrefurl=[^&]+|(?:q|url)=https?://(?!(?:\w+\.)*google\.com)[^&]+'),
            'duckduckgo': re.compile('uddg=https?[^&]+'),
            'yahoo'     : re.compile('https?://(?!(?:\w+\.)*yahoo\.com)'),
        }

        dom = BeautifulSoup(self.page, 'html.parser')
        for a in dom.find_all('a'):
            href = a.get('href')
            if href is None: continue
            if self.engine == 'yahoo':
                if re.match(query_regex['yahoo'], href): urls.append(href)
            else:
                query = parse_url(href).query
                if query is None: continue
                matched = re.search(query_regex[self.engine], query)
                if matched is not None:
                    url = matched.group().split('=')[1]
                    if self.engine == 'duckduckgo': url = self._decode_url(url)
                    if not url in urls: urls.append(url)
        return urls

    def next(self):
        if self.index == 1:
            response  = self.session.get(self.url, headers = Search.headers)
            if response.status_code == requests.codes.ok:
                self.page = response.text
                return self._extract_links()
            else:
                return None

        target_content = 'Suivant|Next'
        if self.engine == 'google' or self.engine == 'yahoo':
            hint = goto(tag_regex = target_content, content = self.page)
        else:
            hint = goto(submit_value = target_content, content = self.page)
        if hint is None: return None

        if isinstance(hint, dict):
            response = self.session.post(hint[post], data = hint[payload], headers = Search.headers)
        elif isinstance(hint, str):
            response = self.session.get(link, headers = Search.headers)

        if response.status_code == requests.codes.ok:
            self.page = response.text
            self.index += 1
            return self._extract_links()
        return None

    def previous(self):
        pass

    def get_links(self, count):
        pass
