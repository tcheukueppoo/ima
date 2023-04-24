import sys
import random
import re
import ansi.cursor as c

from math import inf

from .image   import Image
from .search  import Search
from .options import ParseOptions
from .        import exceptions as e

from .utils import (
    draw_bar,
    rewrite_text,
    hide_cursor,
    show_cursor
)

ask = (
    'HIGH RESOLUTION IMAGES OF {0}',
    'IMAGES OF {0}',
    'I WANT IMAGES OF {0}',
    'DOWNLOAD IMAGES OF {0}',
    'FREE DOWNLOAD IMAGES OF {0}',
)

def main():
    def _error(error):
        print(sys.argv[0] + ': ' + error, file = sys.stderr)

    def _info(info, **kargs):
        print(info, file = sys.stdout, **kargs)

    opts, args = ParseOptions()
    if len(args) == 0:
        _error("No query string, try `{0} --help' for more info")
        exit(1)

    search = Search(engine = opts.engine, save = False)

    trys = 0
    def _conn_handler():
        nonlocal trys
        if opts.trys == trys:
            show_cursor()
            exit(1)
        trys += 1
        _error('[Warn] Failed to connect, trying to reconnect')

    def _interrupt_handler():
        _error('^Interrupted')
        show_cursor()
        exit(1)

    hide_cursor()
    for query in args:
        search.set_engine(random.choice(ask).format(query))

        results = []
        n = 0
        while True:
            try:
                results = search.next(as_image = False if opts.search else True)

                if opts.search:
                    for url in results:
                        n += 1
                        _info(url if len(args) == 1 else '{0},{1}'.format(query, url))
                        if opts.n == n:
                            show_cursor()
                            exit(0)

                for image in results:
                    _info('[Website] {0}'.format(image.base_url))

                    image_links = []
                    while True:
                        try:
                            if len(image_links) < opts.image_count:
                                for link in image.get_links(
                                    opts.image_count,
                                    min_score   = opts.score,
                                    use_content = opts.check_image
                                ):
                                    if opts.verbose:
                                        _info('[Found] {0}'.format(link))
                                    if image_links.count(link) == 0:
                                        image_links.append(link)
                                    if len(image_links) == opts.image_count:
                                        break
                            i = 0
                            while True:
                                filename = None
                                try:
                                    if i != 0 and filename is not None:
                                        _info('Retrying to download {0}'.format(filename))

                                    while n != opts.n and i < len(image_links):

                                        if opts.image_link:
                                            hash = { 'd': 'content', 'l': 'url', 's': 'score' }
                                            _info(re.sub(r'(?<!\\)\{(l|s|d)\}', lambda m: image_links[i][hash[m.group(1)]], opts.image_link))
                                            n += 1
                                            continue

                                        length, size = 0, 0
                                        for stat in image.download_from(
                                            image_links[i],
                                            path      = opts.dest_dir,
                                            overwrite = opts.overwrite
                                        ):
                                            if len(stat.keys()) == 1:
                                                perc_read = stat['%']
                                                if size == 0 or not opts.progress:
                                                    to_write = perc_read if size > 0 else perc_read
                                                    rewrite_text(to_write, length)
                                                    length = len(to_write)
                                                else:
                                                    draw_bar(perc_read, 30)
                                                continue

                                            filename = stat['filename']
                                            size     = int(stat['size'])
                                            _str     = '[Download] filename: {0}, size: {1}'
                                            _info(_str.format(filename, size), end = '')

                                        n += 1
                                        i += 1
                                    break
                                except KeyboardInterrupt:
                                    _interrupt_handler()
                                except ConnectionError:
                                    _conn_handler()
                                except e.HTTPResponseError:
                                    _error('[Warn] Http error while downloading {0}'.format(filename))
                                    if not opts.image_link:
                                        image_links.pop(i)

                        except ConnectionError:
                            _conn_handler()
                        except KeyboardInterrupt:
                            _interrupt_handler()
                        except e.HTTPResponseError:
                            _error('[Warn] Http response error, skipping ...')

                show_cursor()
                break

            except ConnectionError:
                _conn_handler()
            except KeyboardInterrupt:
                _interrupt_handler()
            except e.OutOfBoundError:
                show_cursor()
                exit(0)
