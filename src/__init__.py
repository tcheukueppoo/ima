import sys
import random
import re

from .image   import Image
from .search  import Search
from .options import ParseOptions
from .        import exceptions
from .utils   import (
    get_base_url,
    # ...
)

ask = [
    'High Resolution Images Of {0}',
    'Images Of {0}',
    'I Want Images Of {0}',
    'Download Images Of {0}',
    'Free Download Images Of {0}',
]

def main():
    opts, args = ParseOptions()

    def _error(error):
        me = sys.argv[0]
        print(me + ': ' + error, file = sys.stderr)
        exit(1)

    def _info(info):
        print(info, file = sys.stdout)

    search = Search(engine = opts.engine, save = False)
    if len(args) == 0:
        _error("No query string, try `{0} --help' for more info".format(me))

    for query in args:
        search.set_engine(query)

        results = []
        trys, count = 0, 0
        while count < opts.count:
            try:
                while count < opts.count:
                    if len(result) < opts.result_count:
                        result += search.next(as_image = True if opts.image_link else False)
                        result = result[0:opts.result_count]

                    if opts.search is not None:
                        for url in result:
                            if count == opts.count: break
                            if len(args) == 1:
                                print(url, file = sys.stdout)
                            else:
                                print('{0},{1}'.format(query, url), file = sys.stdout)
                            count += 1
                        continue

                    for i in range(0, len(result)):
                        image = result.pop(i)
                        _info('[Website] {0}'.format(image.base_url))
                        if opts.image_link:
                            hash = { 'd': 'content', 'l': 'url', 's': 'score' }
                            links = image.get_links(count = opts.image_count)
                            for link in links:
                                out = re.sub(r'(?<!\\)\{(l|s|d)\}', lambda m: link[hash[m.group(1)]], opts.image_link)
                                print(out, file = sys.stdout)
                                count += 1
                        else:
                            try:
                                for stat in image.download(count = opts.image_count):
                                    if len(stat) == 1:

                                        continue
                                    # Head
                                    _info('[download] filename: {0}, size: {1}'.format(stat['filename'], utils.humanize_bytes(stat['size'])))
                            except ConnectionError:
                                _error('connection error')

            except exceptions.HTTPResponseError:
                _error('http response error')
            except ConnectionError:
                _error('connection error')
    
