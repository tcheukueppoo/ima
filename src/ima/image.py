import re
import requests
import random

from requests.exceptions import InvalidURL

from bs4  import BeautifulSoup
from math import inf

from . import utils

encoding = utils.preferred_encoding()

class Image:

    @staticmethod
    def builtin_score(subject, content):
        if content is None or subject is None: return 0

        score   = 0
        content = content.casefold()
        for token in re.split(r'\s+', subject):
            token = token.casefold()
            if content.find(token.casefold()) != -1:
                score += 1
        return score

    def __init__(self, **kargs):
        self.url      = kargs.get('url', '')
        self.base_url = utils.get_base_url(self.url)
        self.session  = requests.Session()
        self.timeout  = kargs.get('timeout', 10)
        self.subject  = kargs.get('subject')

        self.session.headers.update(utils.generate_headers())

    def set_url(self, url):
        self.url      = url
        self.base_url = utils.get_base_url(url)


    def _get_link(self, tag_object, attributes, **kargs):
        score_link  = kargs.get('score_with', Image.builtin_score)
        min_score   = kargs.get('min_score', 0)
        use_content = kargs.get('use_content', True)

        content = tag_object.get('alt') if tag_object.string == None else tag_object.string.encode(encoding).decode(encoding)
        if use_content and content is None:
            return

        site_name = re.match(r'https?://(?:www\.)?([^.]+)', self.base_url).group(1)
        for attribute in attributes:
            url = tag_object.get(attribute)
            if not url:
                continue

            if attribute == 'srcset':
                # Just pick the first URL, NO OVERHEAD
                matched = re.search(r'\s*((?:https?:|/)?\S+(?<!,))\s*,?\s*(?:\d+(?:\.\d+)?(?:w|x))?', url)
                if not matched:
                    continue
                url = matched.group(1)
            else:
                if re.match('#|javascript:', url):
                    continue
                logo_regex = '/(?:[A-Za-z0-9]+[-_])*(?:logo|' + site_name + ')(?:[-_]?[A-Za-z0-9]+)*\\.' + '(:?' + '|'.join(utils.MIMETYPE_EXT.values()) + ')'
                if re.search(logo_regex, url):
                    continue

            if re.search(r'\.(?:gif|svg)$', url):
                continue
            if url.startswith('/'):
                url = utils.prepend_base_url(self.base_url, url)
            elif not ( url.startswith('data:image/') or url.startswith('http') ):
                continue

            if ( mime_type := utils.is_image(url, self.session, timeout = self.timeout) ) and (
                (score := score_link(self.subject, content)) >= min_score
            ):
                return {
                    'url': url,
                    'content': content if use_content else None,
                    'score': score,
                    'mime': mime_type,
                }

    def get_links(self, n = inf, **kargs):
        links     = []
        n         = inf if n is None else n
        self.page = utils.http_x('GET', self.session, self.url, timeout = self.timeout).text
        dom       = BeautifulSoup(self.page, 'html.parser')

        i     = 0
        links = []
        for tag_attributes in [
            [ 'img', [ 'data-src', 'src', 'srcset' ] ],
            '''[ 'a', [ 'href' ] ],'''
        ]:
            if i == n: break

            tag_objects = dom.find_all(tag_attributes[0])
            while i != n and len(tag_objects) > 0:
                j = random.choice( list(range(0, len(tag_objects))) )

                link = self._get_link(
                    tag_objects[j],
                    tag_attributes[1],
                    **kargs
                )
                if link and len( list(filter(lambda l: l == link, links)) ) == 0:
                    i += 1
                    links.append(link)
                    yield link

                tag_objects.pop(j)

    def download_from(self, link, **kargs):
        url, mime = None, None

        if isinstance(link, dict):
            url  = link.pop('url', None)
            mime = kargs.get('mime_type', None)
            if mime is None:
                mime = link.pop('mime')
        elif isinstance(link, str):
            url = link

        if url is None:
            raise requests.exceptions.InvalidURL
        return utils.download_image(url, self.session, mime_type = mime, **kargs) 
            
    def download(self, **kargs):
        n = kargs.pop('n', inf)

        for link in self.get_links(n):
            for stat in utils.download_image(
                link['url'],
                self.session,
                mime_type = link['mime'],
                **kargs
            ):
                yield stat
