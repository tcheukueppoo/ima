#!/usr/bin/env python

import re
import requests

from urllib3.util import parse_url
from bs4          import BeautifulSoup
from base64       import b64decode, b64encode
from stat         import S_ISREG

from os import (
    curdir,
    getenv,
    makedirs,
    sep,
    stat,
    unlink,
    rename
)

from .exceptions import (
    OutOfBoundError,
    UnsupportedEngine,
    CannotGoBack
)

from .      import utils
from .image import Image

class Search:

    # Static Vars
    encoding = utils.preferred_encoding()

    search_urls = {
        'yahoo': 'https://search.yahoo.com/search/?p={0}',
        'duckduckgo': 'https://html.duckduckgo.com/html/?q={0}',
        'google': 'https://www.google.com/search?q={0}',
    }

    @staticmethod
    def check_engine(engine):
        if not engine in Search.search_urls.keys():
            raise UnsupportedEngine

    @staticmethod
    def get_url(engine, query):
        return Search.search_urls[engine].format(query.replace(' ', '+'))

    @staticmethod
    def _b64decode_str(_str):
        return b64decode(_str.encode(Search.encoding)).decode(Search.encoding)

    @staticmethod
    def _b46encode_str(_str):
        return b64encode(_str.encode(Search.encoding)).decode(Search.encoding)

    def __init__(self, **kargs):
        self.engine = kargs.get('engine', 'google')
        Search.check_engine(self.engine)

        self.href_id = None
        self.query   = kargs.get('query', '')
        self.url     = Search.get_url(self.engine, self.query)
        self._set_base_url()

        self.session = requests.Session()
        self.session.headers.update(utils.generate_headers())
        self.timeout = kargs.get('timeout', 10)

        self.page      = ''
        self.index     = kargs.get('index', 0)
        self.save      = kargs.get('save', True)
        self.save_path = kargs.get('save_path', getenv('HOME', curdir))
        self._set_save_file()

    def _set_base_url(self):
        self.base_url = utils.get_base_url(Search.search_urls[self.engine])

    def _set_save_file(self):
        if S_ISREG(stat(self.save_path)[0]):
            self.save_file = self.save_path
            return

        self.save_file = re.match('(.+)' + sep + '?$', self.save_path).group(1) + sep + '.ima_cache'

    def set_query(self, query):
        self.query = query
        self.url   = Search.get_url(self.engine, self.query)
        self.index = 0

        return self

    def set_engine(self, engine):
        Search.check_engine(engine)

        self.index  = 0
        self.engine = engine
        self.url    = Search.get_url(self.engine, self.query)
        self._set_base_url()

        return self

    def set_url(self, url):
        self.url = url

        return self

    def _decode_url(self, url):
        return re.sub(r'%([a-fA-F0-9]{2})', lambda m: bytearray.fromhex(m.group(1)).decode(Search.encoding), url)

    def _extract_links(self):
        img_ext    = '\.' + '|'.join(utils.MIMETYPE_EXT.keys()) + '$'
        href_regex = {
            'google': [
                r'imgrefurl=[^&]+|(?:q|url|u)=https?://(?!(?:\w+\.)*google\.com)[^&]+',
                r'https://(?!(?:(?:\w+\.)*google\.com))',
            ],
            'yahoo': [
                r'https://r\.search\.yahoo\.com/.+/RO=\d+/RU=([^/]+)',
                r'https://(?!(?:(?:\w+\.)*yahoo\.(?:uservoice\.)?|(?:(?P<n>cc\.)|www\.)bing(?(n)j)\.)com)',
            ],
            'duckduckgo': [
                r'uddg=https?[^&]+',
                r'https://(?!(?:(?:\w+\.)*duckduckgo\.com))',
            ],
        }

        urls = set()
        dom  = BeautifulSoup(self.page, 'html.parser')
        for a in dom.find_all('a'):
            href = a.get('href')

            if href is None or not re.match('https?://', href):
                continue
            if self.engine == 'yahoo':
                matched = re.match(href_regex[self.engine][0], href)
                if matched:
                    url = self._decode_url(matched.group(1))
                    if re.match(href_regex[self.engine][1], url):
                        urls.add(url)
                continue

            if query := parse_url(href).query:
                matched = re.search(href_regex[self.engine][0], query) 
                if matched:
                    url = self._decode_url(matched.group().split('=')[1])
                    if not re.search(img_ext, url):
                        urls.add(url)

            elif re.match(href_regex[self.engine][1], href):
                urls.add(href)
        return urls

    def _get_request_data(self, sense):
        if self.engine == 'duckduckgo':
            return utils.get_post_data(self.page, '/html/', sense.capitalize())

        href_regex = {
            'google': r'/search\?q=[^&]+&.*(?<=&)start=(\d+)&',
            'yahoo': r'https://search\.yahoo\.com/search;[^?]+\?p=[^&]+&.*(?<=&)b=(\d+)&',
        }

        hrefs = utils.match_hrefs(self.page, href_regex[self.engine])
        if hrefs is None: return

        if len(hrefs) == 1:
            if sense == 'back':
                raise CannotGoBack
            return hrefs[0]['href']

        hrefs.sort(key = lambda m: m['id'])
        if len(hrefs) == 2:
            return hrefs[ 1 if sense == 'next' else 0 ]['href']

        #old          = self.href_id
        request_data = None
        for c in range(0, len(hrefs)):
            if not self.href_id:
                self.href_id = hrefs[c]['id']
                request_data = hrefs[c]['href']
                break

            #print("See: ", hrefs[c]['id'], ' and ', self.href_id)
            if self.href_id < hrefs[c]['id']:
                if sense == 'previous':
                    self.href_id = hrefs[c - 2]['id']
                    request_data = hrefs[c - 2]['href']
                else:
                    self.href_id = hrefs[c]['id']
                    request_data = hrefs[c]['href']
                break

            if sense == 'previous' and (
                self.href_id > hrefs[-1]['id'] or (
                    self.href_id == hrefs[-1]['id'] and c == (len(hrefs) - 1)
                )
            ):
                href         = hrefs[-2] if hrefs[-1]['id'] == self.href_id else hrefs[-1]
                self.href_id = href['id']
                request_data = href['href']
                break

        #print("id: ", old, "new id: ", self.href_id)
        #print("last: ", hrefs[-1])
        return request_data

    def _load_page(self, request_data):
        # Simple link to follow
        if isinstance(request_data, str):
            self.page = utils.http_x(
                'GET',
                self.session,
                utils.prepend_base_url(self.base_url, request_data),
                timeout = self.timeout
            ).text

        # HTTP POST, DuckDuckGO
        elif isinstance(request_data, dict):
            self.page = utils.http_x(
                'POST',
                self.session,
                utils.prepend_base_url(self.base_url, request_data['action']),
                data    = request_data['payload'],
                timeout = self.timeout
            ).text

    def _convert_links_to_image_objects(self, links):
        for link in links:
            yield Image(subject = self.query, url = link)

    def next(self, **kargs):
        save     = kargs.get('save', self.save)
        as_image = kargs.get('as_image', False)

        if self.index == 0:
            self.page = utils.http_x('GET', self.session, self.url, timeout = self.timeout).text
        else:
            request_data = self._get_request_data('next')
            if request_data is None:
                raise OutOfBoundError
            self._load_page(request_data)

        self.index += 1
        links = self._extract_links()
        if save:
            self._save(links)

        if as_image:
            return self._convert_links_to_image_objects(links)
        return list(links)

    def back(self, **kargs):
        save     = kargs.get('save', self.save)
        as_image = kargs.get('as_image', False)

        if self.index == 1 or self.index == 0:
            raise OutOfBoundError
        
        self._load_page(self._get_request_data('previous'))
        self.index -= 1

        links = self._extract_links()
        if save:
            self._save(links)

        if as_image:
            return self._convert_links_to_image_objects(links)
        return list(links)

    def get_links(self, n = 5, **kargs):
        if n < 1: raise OutOfBoundError

        links    = []
        save     = kargs.get('save', self.save)
        start    = kargs.get('start', True)
        as_image = kargs.get('as_image', False)

        if start is True:
            self.index = 1

        while len(links) < n:
            try:
                new_links = self.next()
                links += new_links
            except OutOfBoundError:
                break

        links = links[0:n]
        if save and len(links) > 0:
            self._save(links)

        if as_image is not None:
            return self._convert_links_to_image_objects(links)
        return links

    def _save(self, links):
        file       = self.save_file
        tmp_file   = file + '_tmp'
        links      = list(links)
        found_file = True

        makedirs(self.save_path, exist_ok = True)
        try:
            fd = open(file, 'r')
        except FileNotFoundError:
            found_file = False
            tmp_fd     = open(file, 'w')
        else:
            tmp_fd = open(tmp_file, 'w')

            while record := fd.readline():
                query, link, frequency = re.split(',', record)
                query, link = Search._b64decode_str(query), Search._b64decode_str(link)
                exists = False

                i = 0
                while i < len(links):
                    if link == links[i] and self.query == query:
                        frequency = str(int(frequency) + 1)
                        tmp_fd.write(re.match('(.+),', record).group(1) + ',' + frequency + "\n")
                        links.pop(i)
                        exists = True
                    i += 1
                if not exists:
                    tmp_fd.write(record)
        finally:
            for link in links:
                query = Search._b46encode_str(self.query)
                link  = Search._b46encode_str(link)
                tmp_fd.write('{0},{1},1\n'.format(query, link))

        if found_file:
            unlink(file)
            rename(tmp_file, file)

    def query_saves(self, **kargs):
        query      = kargs.get('query')
        query_like = kargs.get('query_like')
        frequency  = kargs.get('frequency')

        matched = []
        fd = open(self.save_file, 'r')
        while record := fd.readline():
            splited = list( map(Search._b64decode_str, re.split(',', record)) )

            if (
                 query and splited[0] == query
               ) or (
                 query_like and re.match(query_like, splited[0])
               ) or (
                 frequency and frequency == splited[2]
            ):
                matched += splited[1]
        return matched
