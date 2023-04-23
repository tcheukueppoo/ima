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
                results = search.next(as_image = False if opts.search else True)

                if opts.search:
                    for url in results:
                        c += 1
                        _info(url if len(args) == 1 else '{0},{1}'.format(query, url))
                        if opts.count == c:
                            exit(0)
                hash = { 'd': 'content', 'l': 'url', 's': 'score' }
                for image in results:
                    if opts.verbose:
                        _info('[Website] {0}'.format(image.base_url))

                    image_links = list()
                    while True:
                        try:
                            cc = c
                            image_links = []

                            for link in image.get_links(count = opts.count):
                                cc += 1
                                image_links.append(link)
                                if cc == opts.count: break
                            i = 0
                            while True:
                                filename = None
                                try:
                                    im = i
                                    while opts.count != c and im < len(image_links):
                                        if opts.image_link:
                                            c += 1
                                            def trans(m):
                                                return image_links[im][hash[m.group(1)]]
                                            _info(re.sub(r'(?<!\\)\{(l|s|d)\}', trans, opts.image_link))
                                            continue

                                        link = image_links[im]
                                        url = link.pop('url')
                                        for stat in image.download_from(
                                            url,
                                            path      = opts.dest_dir,
                                            overwrite = opts.overwrite,
                                            **link
                                        ):
                                            if len(stat.keys()) == 1:
                                                pass
                                            _str = '[Download] filename: {0}, size: {1}'
                                            _info(_str.format(stat['filename'], utils.humanize_bytes(stat['size'])))
                                        c  += 1
                                        i  += 1
                                        im += 1
                                    break
                                except ConnectionError:
                                    pass
                        except ConnectionError:
                            _error('[WARN] Failed to connect, trying to reconnect')
                            if trys == opts.trys: exit(1)
                            trys += 1
                break
            except exceptions.OutOfBoundError:
                exit(0)
            except ConnectionError:
                _error('[WARN] Failed to connect, trying to reconnect') 
                if trys == opts.trys: exit(1)
                trys += 1
