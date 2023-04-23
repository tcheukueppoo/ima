import sys
import random
import re

from math     import inf
from .image   import Image
from .search  import Search
from .options import ParseOptions
from .        import exceptions
from .utils   import (
    humanize_bytes,
    term_print,
)

ask = [
    'HIGH RESOLUTION IMAGES OF {0}',
    'IMAGES OF {0}',
    'I WANT IMAGES OF {0}',
    'DOWNLOAD IMAGES OF {0}',
    'FREE DOWNLOAD IMAGES OF {0}',
]

def main():
    opts, args = ParseOptions()

    def _error(error):
        me = sys.argv[0]
        print(me + ': ' + error, file = sys.stderr)

    def _info(info):
        print(info, file = sys.stdout)

    search = Search(engine = opts.engine, save = False)
    if len(args) == 0:
        _error("No query string, try `{0} --help' for more info")
        exit(1)

    for query in args:
        search.set_engine(ask[1].format(query))

        results = []
        trys, c = 0, 0
        while True:
            try:
                while True:
                    results = search.next(as_image = False if opts.search else True)

                    if opts.search:
                        for url in results:
                            c += 1
                            _info(url if len(args) == 1 else '{0},{1}'.format(query, url))
                            if opts.count == c: exit(0)

                    for image in results:
                        image_links = list()

                        if opts.verbose:
                            _info('[Website] {0}'.format(image.base_url))

                        while True:
                            try:
                                cc = c
                                image_links = []
                                for link in image.get_links(count = opts.count):
                                    cc += 1
                                    image_links.append(link)
                                    if cc == opts.count: break
                                break
                            except ConnectionError:
                                _error('[WARN] Failed to connect, trying to reconnect')
                                if trys == opts.trys: exit(1)
                                trys += 1

                            while True:
                                i= 0
                                filename = None
                                try:
                                    while opts.count != c and (im := range(i, len(image_links))):
                                        if opts.image_link:
                                            hash = { 'd': 'content', 'l': 'url', 's': 'score' }
                                            _info(re.sub(r'(?<!\\)\{(l|s|d)\}', lambda m: image_links[im][hash[m.group(1)]], opts.image_link))
                                        c += 1
                                        continue
                                    for stat in image.download_from(image_links[im]):
                                        if len(stat) = 1:
                                            pass
                                        # Header
                                        filename = stat['filename']
                                        _info(
                                            '[Download] filename: ' +
                                            stat['filename']        +
                                            ', size: '              +
                                            utils.humanize_bytes(stat['size'])
                                        )
                                        c += 1
                                        i += 1
                                except ConnectionError:
                                    pass
                            
                exit(0)
            except exceptions.OutOfBoundError:
                exit(0)
            except ConnectionError:
                _error('[WARN] Failed to connect, trying to reconnect') 
                if trys == opts.trys: exit(1)
                trys += 1
