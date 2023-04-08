import re

from bs4    import BeautifulSoup
from math   import inf
from .utils import download_file, prepend_base_url, is_image, http_x, preferred_encoding, get_baseçurl, generate_headers


class Image:

    # Static variables
    encoding = preferred_encoding()

    def __init__(self, **kargs):
        self.url      = kargs.get('url', '')
        self.baseçurl = get_base_url(url)
        self.session  = request.Session()
        self.subject  = kargs.get('subject')

        self.session.update(headers = generate_headers())

    def set_url(self, url):
        self.url      = url
        self.base_url = get_base_url(url)

    @staticmethod
    def _uniquefy_links(links):
        uniq_links = []

        while True:
            uniq_link = links.pop(0)

            i = 1
            while i < len(links):
                if links[i]['url'] == uniq_link['url']:
                    candidate = links.pop(i)

                    if candidate['score'] > uniq_link['score']:
                        uniq_link = candidate
                i += 1

            uniq_links.append(uniq_link)
            if len(links) == 0: break

        return uniq_links

    def _builtin_score(self, links):
        for token in re.split('\s+', self.subject):
            for link in links:
                if link['content'].casefold().find(token.casefold()) != -1:
                    link['score'] += 1

        return links

    def _get_link(self, tag_object, tag, attribute):
        a_content   = None if tag_object.string == None else tag_object.string.encode(encoding).decode(encoding)
        get_content = { 'a': a_content, 'img': tag_object.get('alt') }
        content     = get_content[tag]
        url         = tag_object.get(attribute)

        if content is None or url is None or re.match('#', url):
            return None

        # is url a data URI
        if not url.startswith('data:'):
            url = prepend_base_url(self.base_url, url)
            if is_image(url, self.session) is False:
                return None

        return {
            'score'  : 0,
            'content': content,
            'url'    : url,
        }

    def get_links(self, **kargs):
        if self.page is None:
            return None

        links       = []
        score_links = kargs.get('score_with', self._builtin_score)
        count       = kargs.get('count', inf)

        self.page = utils.http_x(
            'GET',
            self.session,
            self.url
        )

        dom = BeautifulSoup(self.page, 'html.parser')
        for tag_attribute in [ ['img', 'src'], [ 'a', 'href' ] ]:
            for tag_object in dom.find_all(tag_attribute[0]):
                if link := self._get_link(tag_object, *tag_attribute):
                    links.append(link)

        if len(links) == 0:
            return None

        if self.subject is not None:
            links = score_links(links)

        # NOTE: Get unique links *after* scoring!
        links = Image._uniquefy_links(links)
        links.sort(key = lambda m: m['score'], reverse = True)

        return links[0:count]

    def download_from(self, link, **kargs):
        download_file(link, session, **kargs)

    def download(self, **kargs):
        if links := self.get_links(**kargs):
            for link in links:
                self.download_from(link['url'])
