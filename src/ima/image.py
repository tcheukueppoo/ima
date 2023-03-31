from bs4    import BeautifulSoup
from .utils import download_file, prepend_base_url
from math   import inf

import re, requests

class Image:
    def __init__(self, **kargs):
        self.base_url = kargs.get('base_url', '')
        self.page     = kargs.get('page', '')
        self.subject  = kargs.get('subject')

    def _is_image(self, link, **kargs):
        session  = kargs.get('session', requests.session())
        response = session.head(link)
        if re.match('image/', response.headers.get('content-type', '')): return True
        return False

    def _score_image(self, link_content):
        pass

    def _get_link_content(self, tag_object, tag, attribute):
        if tag_object.get(attribute) is None: return []
        link = prepend_base_url(self.base_url, tag_object.get(attribute))
        if self._is_image(link): return [ link, tag_object.string ]
        return []

    def get_links(self, **kargs):
        links         = []
        count         = kargs.get('count', inf)
        score         = kargs.get('score')
        builtin_score = kargs.get('builtin_score', True)
        dom           = BeautifulSoup(self.page, 'html.parser')

        for tag_object in dom.find_all('img'):
            links += self._get_link_content(tag_object, 'img', 'src')
        for tag_object in dom.find_all('a'):
            links += self._get_link_content(tag_object, 'a', 'href')

        return links if len(links) > 0 else None

    def download_image(self, count = 1):
        pass

    def download_image_from(self, **links):
        pass
        
