#!/usr/bin/env python

import re, requests

from urllib3.util import parse_url
from bs4          import BeautifulSoup
from .image       import Image
from .utils       import give_hint
from base64       import b64decode, b64encode, b64encode
from os           import curdir, getenv, makedirs, sep

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
        self.engine = kargs.get('engine', 'google')
        Search.check_engine(self.engine)

        self.query = kargs.get('query', '')
        self.url   = Search.get_url(self.engine, self.query)
        self._set_base_url()

        self.page      = ''
        self.index     = kargs.get('index', 1)
        self.save      = kargs.get('save', True)
        self.save_path = kargs.get('save_path', getenv('HOME', curdir))
        self.session   = requests.Session()

    def _set_base_url(self):
        self.base_url = re.match(r'(.+?)(?<!/)/(?!/)', Search.search_urls[self.engine]).group(1)

    def set_query(self, query):
        self.query = query
        self.url   = Search.get_url(self.engine, self.query)
        return self

    def set_engine(self, engine):
        Search.check_engine(engine)
        self.engine = engine
        self.url    = Search.get_url(self.engine, self.query)
        self._set_base_url()
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
            'google'    : r'imgrefurl=[^&]+|(?:q|url)=https?://(?!(?:\w+\.)*google\.com)[^&]+',
            'duckduckgo': r'uddg=https?[^&]+',
            'yahoo'     : r'https?://(?!(?:\w+\.)*yahoo\.com)',
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

    def _load_page(self, hint):
        if isinstance(hint, dict):
            hint['action'] = prepend_base_url(self.base_url, hint['action'])
            response = self.session.post(hint['action'], data = hint['payload'], headers = Search.headers)
        elif isinstance(hint, str):
            hint = self._prepend_base_url(hint)
            response = self.session.get(hint, headers = Search.headers)

        if isinstance(response, requests.Response) and response.status_code == requests.codes.ok:
            self.page = response.text
            return True
        return False

    def _give_hint(self, sense):
        misc = {
            'next': {
                'google':     { 'tag_content': 'Next' },
                'duckduckgo': { 'submit_value': 'Next', 'action': '/html' },
                'yahoo':      { 'index': self.index + 1 },
            },
            'previous': {
                'google':     { 'tag_content': 'Previous' },
                'duckduckgo': { 'submit_value': 'Previous', 'action': '/html' },
                'yahoo':      { 'index': self.index - 1 },
            },
        }

        hint = give_hint(page = self.page, **misc[sense][self.engine])
        if hint is None:
            error = """
                UnexpectedError: possible issues might be
                 1. Reached the end of the page
                 3. Code isn't familiar with the page structure, needs to adapt
            """
            raise Exception(error)
        return hint

    def next(self, **kargs):
        if self.index == 1:
            response = self.session.get(self.url, headers = Search.headers)
            if response.status_code == requests.codes.ok:
                self.page = response.text
            else:
                raise Exception("FetchError: couldn't fetch the first page")
        else:
            self._load_page(self._give_hint('next'))
        save = kargs.get('save', self.save)
        self.index += 1
        links = self._extract_links()
        if save: self._save(links)
        return links

    def previous(self, **kargs):
        if self.index == 1:
            raise Exception('OutOfBoundError: already at the start page')
        else:
            self._load_page(self._give_hint('previous'))
        save = kargs.get('save', self.save)
        self.index -= 1
        links = self._extract_links()
        if save: self._save(links)
        return links

    def get_nlinks(self, **kargs):
        count = kargs.get('count', 1)
        if count < 1: raise Exception('CountError: number of links to fetch must be > 0')

        current_trys = 0
        links        = []
        save         = kargs.get('save', self.save)
        start        = kargs.get('start', True)
        trys         = kargs.get('trys', 2)

        if start is True: self.index = 1
        while len(links) < count or current_trys < trys:
            try:
                links += self.next()
            except:
                current_trys += 1
        links = links if len(links) < count else links[0:count]
        if save: self._save(links)
        return links

    def _save(self, links):
        makedirs(self.save_path)
        file     = re.match('(.+)' + sep + '?$', self.save_path).group(1) + sep + '.ima_cache'
        tmp_file = file + '_tmp'
        with open(tmp_file, 'w') as tmp_fd, open(file, 'r') as fd:
            while record := fd.readline():
                query, link, frequency = re.split(',', record)
                query = b64decode(query)
                link  = b64decode(link)
                exists = False
                for i in range(0, len(links)):
                    if link == links[i] and self.query == query:
                        frequency += 1
                        tmp_fd.write(b64encode(query) + ',' + b64encode(link) + ',' + frequency)
                        links.pop(i)
                        exists = True
                if not exists: tmp_fd.write(record)
            for link in links:
                tmp.fd.write(b64encode(query), + ',' + b64encode(link) + ',1')
        unlink(file)
        rename(tmp_file, file)
        
