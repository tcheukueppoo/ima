import re
import requests

from bs4    import BeautifulSoup
from math   import inf
from .      import utils

encoding = utils.preferred_encoding()

class Image:

    def __init__(self, **kargs):
        self.url      = kargs.get('url', '')
        self.base_url = utils.get_base_url(self.url)
        self.session  = requests.Session()
        self.subject  = kargs.get('subject')

        self.session.headers.update(utils.generate_headers())

    def set_url(self, url):
        self.url      = url
        self.base_url = utils.get_base_url(url)

    @staticmethod
    def _uniquefy_links(links):
        uniq_links = []

        while len(links) != 0:
            uniq_link = links.pop(0)

            i = 0
            while i < len(links):
                i += 1
                if links[i]['url'] != uniq_link['url']:
                    continue
                candidate = links.pop(i)
                if candidate['score'] > uniq_link['score']:
                    uniq_link = candidate

            uniq_links.append(uniq_link)

        return uniq_links

    def _builtin_score(self, links):
        for token in re.split('\s+', self.subject):
            for link in links:
                if link['content'].casefold().find(token.casefold()) != -1:
                    link['score'] += 1

        return links

    def _get_link(self, tag_object, tag, attribute):
        content   = tag_object.get('alt') if tag_object.string == None else tag_object.string.encode(encoding).decode(encoding)
        url       = tag_object.get(attribute)
        mime_type = None

        if content is None or url is None or re.match('#|javascript:', url):
            return None

        url = url if url.startswith('data:image/') else utils.prepend_base_url(self.base_url, url)
        if not ( url and ( mime_type := utils.is_image(url, self.session) ) ):
            return None

        return {
            'score'  : 0,
            'content': content,
            'url'    : url,
            'mime'   : mime_type,
        }

    def get_links(self, **kargs):
        links       = []
        score_links = kargs.get('score_with', self._builtin_score)
        count       = kargs.get('count', inf)
        sort        = kargs.get('sort', False)

        self.page = utils.http_x(
            'GET',
            self.session,
            self.url
        )

        dom = BeautifulSoup(self.page, 'html.parser')
        for tag_attribute in [ [ 'img', 'src' ], [ 'a', 'href' ] ]:
            for tag_object in dom.find_all(tag_attribute[0]):
                if link := self._get_link(tag_object, *tag_attribute): links.append(link)

        if len(links) == 0:
            return None

        if self.subject is not None:
            links = score_links(links)

        # NOTE: Get unique links *after* scoring!
        links = Image._uniquefy_links(links)
        if sort:
            links.sort(key = lambda m: m['score'], reverse = True)

        return links[0:count]

    def download_from(self, link, **kargs):
        return download_image(
            link if not isinstance(link, dict) else link.get('url', ''),
            session,
            **kargs
        )
            
    def download(self, **kargs):
        links = self.get_links(**kargs)
        if not links: return

        for link in links:
            for percent in self.download_from(
                link['url'],
                self.session,
                mime_type = link['mime'],
                **kargs
            ):
                yield { 'url': link['url'], 'percent': percent }
