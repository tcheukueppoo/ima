import re
import requests

from bs4    import BeautifulSoup
from math   import inf

from requests.exceptions import InvalidURL
from .      import utils

encoding = utils.preferred_encoding()

class Image:

    def __init__(self, **kargs):
        self.url      = kargs.pop('url', '')
        self.base_url = utils.get_base_url(self.url)
        self.session  = requests.Session()
        self.subject  = kargs.pop('subject')

        self.session.headers.update(utils.generate_headers())

    def set_url(self, url):
        self.url      = url
        self.base_url = utils.get_base_url(url)

    def _builtin_score(self, content):
        score   = 0
        content = content.casefold()

        if self.subject:
            for token in re.split('\s+', self.subject):
                token = token.casefold()
                if content.find(token.casefold()) != -1:
                    score += 1
        return score

    def _get_link(self, tag_object, tag, attributes, **kargs):
        score_link  = kargs.pop('score_with', self._builtin_score)
        min_score   = kargs.pop('min_score', 1)
        use_content = kargs.pop('use_content', True)

        content = tag_object.get('alt') if tag_object.string == None else tag_object.string.encode(encoding).decode(encoding)
        if use_content and content is None:
            return

        for attribute in attributes:
            url = tag_object.get(attribute)
            if not url: continue

            if attribute == 'srcset':
                # Just get the first URL, NO OVERHEAD
                if matched := re.search(r'\s*((?:https?:|/)?\S+(?<!,))\s*,?\s*(?:\d+(?:\.\d+)?(?:w|x))?', url):
                    url = matched.groups(1)
            elif re.match('#|javascript:', url):
                continue

            if url.startswith('/'):
                url = utils.prepend_base_url(self.base_url, url)
            elif not ( url.startswith('data:image/') or url.startswith('http') ):
                continue

            if ( mime_type := utils.is_image(url, self.session) ) and (
                (score := score_link(content)) >= min_score
            ):
                link = {
                    'score'  : score,
                    'url'    : url,
                    'mime'   : mime_type,
                }
                if use_content:
                    link['content'] =  content
                return link

    def get_links(self, **kargs):
        links     = []
        count     = kargs.pop('count', inf)
        self.page = utils.http_x('GET', self.session, self.url).text
        dom       = BeautifulSoup(self.page, 'html.parser')

        i     = 0
        done  = False
        links = []
        for tag_attribute in [
            [ 'img', [ 'data-src', 'src', 'srcset' ] ],
            """[ 'a', [ 'href' ] ],"""
        ]:
            for tag_object in dom.find_all(tag_attribute[0]):
                link = self._get_link(
                    tag_object,
                    *tag_attribute,
                    **kargs
                )
                print(link)
                if not link: continue
                if len( list( filter(lambda l: l == link, links) ) ) == 0:
                    i += 1
                    links.append(link)
                    yield link

                if i == count:
                    done = True
                    break
            if done: break

    def download_from(self, link, **kargs):
        if isinstance(link, dict):
            link = link.get('url')
        if not link:
            raise requests.exceptions.InvalidURL
        return utils.download_image(link, self.session, **kargs)
            
    def download(self, **kargs):
        for link in self.get_links(**kargs):
            for percent in utils.download_image(
                link['url'],
                self.session,
                mime_type = link['mime'],
                **kargs
            ):
                yield { 'url': link['url'], 'percent': percent }
