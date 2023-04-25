import sys
import random
import re
import ansi.cursor as c

from math    import inf
from os.path import basename

from requests.exceptions import ConnectionError

from .image   import Image
from .search  import Search
from .options import ParseOptions
from .        import exceptions as e

from .utils import (
    get_base_url,
    draw_bar,
    rewrite_text,
    hide_cursor,
    show_cursor,
    go_down
)

ask = (
    'HIGH RESOLUTION IMAGES OF {0}',
    'IMAGES OF {0}',
    'I WANT IMAGES OF {0}',
    'DOWNLOAD IMAGES OF {0}',
    'FREE DOWNLOAD IMAGES OF {0}',
)

def main():
    me = sys.argv[0]

    def _error(error):
        print('{0}: {1}'.format(me, error), file = sys.stderr)

    def _info(info, **kargs):
        print(info, file = sys.stdout, **kargs)

    opts, args = ParseOptions()
    if len(args) == 0:
        _error("No query string(s), try `{0} -h' for more info.".format(me))
        exit(1)

    trys = 0
    def _connection_handler():
        nonlocal trys
        if opts.retrys == trys:
            _error('Failed to connect.')
            show_cursor()
            exit(1)
        trys += 1
        _error('[Warn] Failed to connect, trying to reconnect.')

    def _interrupt_handler():
        _error('^Interrupted by user.')
        show_cursor()
        exit(1)

    def _in_domains(url):
        if opts.no_domains is None:
            return 0
        return len( list( filter(lambda d: url.endswith(d), re.split(',', opts.no_domains)) ) )

    hide_cursor()
    search = Search(engine = opts.engine, save = False)
    for query in args:
        search.set_query(random.choice(ask).format(query))

        n = 0
        while True:
            try:
                results = search.next(as_image = False if opts.search else True)
                if opts.search:
                    for url in results:
                        if _in_domains(get_base_url(url)): continue
                        _info(url if len(args) == 1 else '{0},{1}'.format(query, url))
                        n += 1
                        if opts.n == n:
                            show_cursor()
                            exit(0)
                    continue

                for image in results:
                    if _in_domains(image.base_url):
                        continue

                    _info('[Website] {0}'.format(image.base_url))

                    image.subject(query)
                    image_links = []
                    while True:
                        try:
                            if len(image_links) < opts.image_count:
                                for link in image.get_links(
                                    opts.image_count,
                                    min_score   = opts.score,
                                    use_content = False if opts.score == 0 else True
                                ):
                                    if len(image_links) == opts.image_count:
                                        break
                                    if opts.n == n:
                                        show_cursor()
                                        exit(1)
                                    if image_links.count(link) != 0:
                                        continue
                                    if opts.verbose:
                                        _info('[Found] {0}'.format(link))

                                    if opts.image_link:
                                        hash = { 'd': 'content', 'l': 'url', 's': 'score' }
                                        _info(re.sub(r'(?<!\\)\{(l|s|d)\}', lambda m: link[hash[m.group(1)]], opts.image_link))
                                        image_links.append(link)
                                        n += 1
                                        continue

                                    while True:
                                        filename = None
                                        try:
                                            if filename is not None:
                                                _info('\nRetrying to download {0}'.format(filename))

                                            # Fallback to default
                                            length, size = 0, ''
                                            for stat in image.download_from(
                                                link,
                                                path      = opts.dest_dir,
                                                overwrite = opts.overwrite,
                                                auto      = opts.auto
                                            ):
                                                if len(stat.keys()) == 1:
                                                    read = stat['%']
                                                    if size.startswith('0') or opts.no_progress is False:
                                                        rewrite_text(read, length)
                                                        length = len(read)
                                                    else:
                                                        draw_bar(read.removesuffix('%'), 30)
                                                        info(read, end = '')
                                                    continue

                                                filename = basename(stat['filename'])
                                                size     = stat['size']

                                                ln   = ' ' if size.startswith('0') or not opts.no_progress else '\n'
                                                _str = '[Download] Filename: {0}, Size: {1}'
                                                _info(_str.format(filename, size), end = ln)

                                            go_down()
                                            n += 1
                                            image_links.append(link)
                                            break
                                        except KeyboardInterrupt:
                                            _interrupt_handler()
                                        except ConnectionError:
                                            _connection_handler()
                                            continue
                                        except e.HTTPResponseError:
                                            _error("[Warn] HTTP error while downloading file {0}".format(filename))
                                            break
                            break
                        except ConnectionError:
                            _connection_handler()
                            continue
                        except KeyboardInterrupt:
                            _interrupt_handler()
                        except e.HTTPResponseError:
                            _error('[Warn] Http error, skipping ...')
                            break
            except ConnectionError:
                _connection_handler()
                continue
            except KeyboardInterrupt:
                _interrupt_handler()
            except e.OutOfBoundError:
                show_cursor()
                exit(0)

            show_cursor()
            break
