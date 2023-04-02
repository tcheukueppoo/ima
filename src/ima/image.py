from bs4    import BeautifulSoup
from math   import inf
from .utils import download_file, prepend_base_url

import re, requests

class Image:
    def __init__(self, **kargs):
        self.base_url = kargs.get('base_url', '')
        self.page     = kargs.get('page', '')
        self.subject  = kargs.get('subject')

    def is_image(self, link, **kargs):
        session  = kargs.get('session', requests.session())
        response = session.head(link)
        if re.match('image/', response.headers.get('content-type', '')): return True
        return False

    def _builtin_score(self, links):
        if self.subject is None: return links
        for token in re.split('\s+', self.subject):
            for link in links:
                if link['content'].find(token) != -1: link['score'] += 1
        return links

    def _get_link(self, tag_object, tag, attribute):
        get_content = { 'a': tag_object.string, 'img': tag_object.get('alt') }
        content     = get_content[tag]
        url         = tag_object.get(attribute)

        if content is None or len(content) == 0 or url is None or re.match('#', url): return None
        #if self.is_image(url) is False: return None
        return {
            'content': content,
            'url'    : prepend_base_url(self.base_url, url),
            'score'  : 0
        }

    def get_links(self, **kargs):
        links       = []
        score_links = kargs.get('score_with', self._builtin_score)
        count       = kargs.get('count', inf)
        dom         = BeautifulSoup(self.page, 'html.parser')

        for tag_attribute in [['img', 'src'], ['a', 'href']]:
            for tag_object in dom.find_all(tag_attribute[0]):
                if (link := self._get_link(tag_object, *tag_attribute)) is not None:
                    links.append(link)

        def sort_key(l): return l['score']
        links = score_links(links)
        # NOTE: Get unique links *after* scoring!
        uniq_links = []
        while True:
            i         = 1
            uniq_link = links.pop(0)
            while i < len(links):
                if links[i]['url'] == uniq_link['url']:
                    candidate = links.pop(i)
                    if candidate['score'] > uniq_link['score']:
                        uniq_link = candidate
                i += 1
            uniq_links.append(uniq_link)
            if len(links) == 0: break
         
        uniq_links.sort(key = sort_key, reverse = True)
        return uniq_links if len(uniq_links) <= count else uniq_links[0:count]

    def download_from(self, link, **kargs):
        download_file(link, **kargs)

    def download(self, **kargs):
        for link in self.get_links(**kargs):
            self.download_from(link['url'])
