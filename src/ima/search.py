#!/usr/bin/env python

import re, requests

from urllib3.util import parse_url
from bs4          import BeautifulSoup
from .image       import Image
from .utils       import give_hint, get_base_url, prepend_base_url, strip_base_url, is_image
from base64       import b64decode, b64encode
from os           import curdir, getenv, makedirs, sep, stat, unlink, rename
from stat         import S_ISREG

class Search:
    search_urls = {
        'duckduckgo': 'https://html.duckduckgo.com/html/?q={0}',
        'google'    : 'https://www.google.com/search?q={0}',
        'yahoo'     : 'https://search.yahoo.com/search/?p={0}'
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
        return Search.search_urls[engine].format(query.replace(' ', '+'))

    def __init__(self, **kargs):
        self.engine = kargs.get('engine', 'google')
        Search.check_engine(self.engine)

        self.query = kargs.get('query', '')
        self.url   = Search.get_url(self.engine, self.query)
        self._set_base_url()

        self.page      = ''
        self.index     = kargs.get('index', 0)
        self.save      = kargs.get('save', True)
        self.session   = requests.Session()
        self.save_path = kargs.get('save_path', getenv('HOME', curdir))
        self._set_save_file()

    def _set_base_url(self):
        self.base_url = get_base_url(Search.search_urls[self.engine])

    def _set_save_file(self):
        if S_ISREG(stat(self.save_path)[0]):
            self.save_file = self.save_path
            return
        self.save_file = re.match('(.+)' + sep + '?$', self.save_path).group(1) + sep + '.ima_cache'

    def set_query(self, query):
        self.query = query
        self.url   = Search.get_url(self.engine, self.query)
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
        def replace(match):
            return bytearray.fromhex(match.group(1)).decode()
        return re.sub(r'%([a-fA-F0-9]{2})', replace, url)

    def _extract_links(self):
        NOT_YAHOO  = r'(https?://(?!(?:(?:\w+\.)*?yahoo\.com|yahoo\.uservoice\.com)).+)$'
        HREF_REGEX = {
            'google'    : r'imgrefurl=[^&]+|(?:q|url)=https?://(?!(?:\w+\.)*?google\.com)[^&]+',
            'duckduckgo': r'uddg=https?[^&]+',
            'yahoo'     : r'https://r\.search\.yahoo\.com/.+/RO=\d+/RU=([^/]+)',
        }

        urls = set()
        dom  = BeautifulSoup(self.page, 'html.parser')
        for a in dom.find_all('a'):
            href = a.get('href')
            if href is None: continue

            if self.engine == 'yahoo':
                matched = re.match(HREF_REGEX[self.engine], href)
                if matched:
                    url = self._decode_url(matched.group(1))
                    if re.match(NOT_YAHOO, url):
                        urls.add(url)
                continue

            added = False # Some Duckduckgo results are more than CLEAN, SANE!
            query = parse_url(href).query
            if query is not None:
                if matched := re.search(HREF_REGEX[self.engine], query):
                    url = self._decode_url(matched.group().split('=')[1])

                    # Google: some urls given via url= parameter are images, strip them off
                    if self.engine != 'google' or not is_image(url, client = self.session):
                        added = True
                        urls.add(url)

            if not added and self.engine == 'duckduckgo' and not href.startswith('/'):
                urls.add(href)
        return urls

    def _load_page(self, hint):
        response = None

        # Simple link to follow
        if isinstance(hint, str):
            hint = prepend_base_url(self.base_url, hint)
            response = self.session.get(hint, headers = Search.headers)

        # HTTP POST, DuckDuckGO
        elif isinstance(hint, dict):
            hint['action'] = prepend_base_url(self.base_url, hint['action'])
            response = self.session.post(hint['action'], data = hint['payload'], headers = Search.headers)

        if response is not None and response.status_code == requests.codes.ok:
            self.page = response.text
            return True
        else:
            raise Exception('HttpResponseError: HTTP Server Response Code: ', response.status_code)

        return False

    def _give_hint(self, sense):
        HREF_LIKE = strip_base_url(self.url) \
                                     .replace('\\', '\\\\') \
                                     .replace('.', '\.') \
                                     .replace('^', '\^') \
                                     .replace('$', '\$') \
                                     .replace('?', '\?') \
                                     .replace('*', '\*') \
                                     .replace('+', '\+') \
                                     .replace('{', '\{') \
                                     .replace('}', '\}') \
                                     .replace('[', '\[') \
                                     .replace(']', '\]') \
                                     .replace('|', '\|') \
                                     .replace('(', '\(') \
                                     .replace(')', '\)') + '&ei=[^&]+&start=\d+&sa=N'

        TAG_CONTENT_NEXT = '\s*' + str(self.index + 1) + '|' + 'Next' + '|' + 'Suivant' + '\s*'            # need to add more ...
        TAG_CONTENT_BACK = '\s*' + str(self.index - 1) + '|' + 'Prev(?:ious)?' + '|' + 'Précédent' + '\s*' # same here ...

        MISC = {
            'NEXT': {
                'yahoo' : { 'tag_content': TAG_CONTENT_NEXT },
                'google': { 
                    'tag_content': TAG_CONTENT_NEXT,
                    'href_like'  : {
                        'index': -1,
                        're'   : HREF_LIKE,
                    }
                },
                'duckduckgo': {
                    'submit_value': 'Next',
                    'action'      : '/html/',
                },
            },
            'BACK': {
                'yahoo' : { 'tag_content': TAG_CONTENT_BACK },
                'google': {
                    'tag_content': TAG_CONTENT_BACK,
                    'href_like'  : {
                        'index': -2,
                        're'   : HREF_LIKE,
                    }
                },
                'duckduckgo': {
                    'submit_value': 'Previous',
                    'action'      : '/html/',
                },
            },
        }

        hint = give_hint(page = self.page, base_url = self.base_url, **MISC[sense][self.engine])
        print("Fucking hint", hint)
        return hint

    def convert_links_to_image_objects(self, links):
        for link in links:
            yield Image(subject = self.query, page = self.session.get(link).text, base_url = get_base_url(link))

    def next(self, **kargs):
        save     = kargs.get('save', self.save)
        as_image = kargs.get('as_image', False)

        if self.index == 0:
            response = self.session.get(self.url, headers = Search.headers)
            if response.status_code == requests.codes.ok:
                self.page = response.text
            else:
                raise Exception('HttpResponseError: HTTP Server Response Code: ', response.status_code)
        else:
            hint = self._give_hint('NEXT')
            if hint is None or self._load_page(hint) is False: return None

        self.index += 1
        links = self._extract_links()
        if save: self._save(links)
        if as_image: return self.convert_links_to_image_objects(links)

        return links

    def back(self, **kargs):
        save     = kargs.get('save', self.save)
        as_image = kargs.get('as_image', False)

        if self.index == 1: return None
        self._load_page(self._give_hint('BACK'))
        self.index -= 1
        links = self._extract_links()
        if save: self._save(links)
        if as_image: return self.convert_links_to_image_objects(links)

        return links

    def get_nlinks(self, **kargs):
        count = kargs.get('count', 1)
        if count < 1: raise Exception('CountError: number of links to fetch must be > 0')

        current_trys = 0
        links        = []
        save         = kargs.get('save', self.save)
        start        = kargs.get('start', True)
        trys         = kargs.get('trys', 2)
        as_image     = kargs.get('as_image', False)

        if start is True: self.index = 1
        while len(links) < count or current_trys < trys:
            new_links = self.next()
            if new_links is None:
                current_trys += 1
                continue
            links += new_links

        links = links[0:count]
        if save: self._save(links)
        if as_image: return self.convert_links_to_image_objects(links)
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
                query  = b64decode(query.encode()).decode()
                link   = b64decode(link.encode()).decode()
                exists = False
                i      = 0
                while i < len(links):
                    if link == links[i] and self.query == query:
                        frequency = str(int(frequency) + 1)
                        tmp_fd.write(re.match('(.+),', record).group(1) + ',' + frequency + "\n")
                        links.pop(i)
                        exists = True
                    i += 1
                if not exists: tmp_fd.write(record)
        finally:
            for link in links:
                tmp_fd.write(b64encode(self.query.encode()).decode() + ',' + b64encode(link.encode()).decode() + ",1\n")
        if found_file:
            unlink(file)
            rename(tmp_file, file)

    def query_saves(self, **kargs):
        query      = kargs.get('query')
        query_like = kargs.get('query_like')
        frequency  = kargs.get('frequency')

        matched = []
        with open(self.save_file, 'r') as fd:
            while record := fd.readline():
                splited    = re.split(',', record)
                splited[0] = b64decode(splited[0].encode()).decode()
                splited[1] = b64decode(splited[1].encode()).decode()
                if query and splited[0] != query: continue
                if query_like and not re.match(query_like, splited[0]): continue
                if frequency and frequency != splited[2]: continue
                matched += splited[1]
        return matched
