import sys
import random
import re

from os.path import basename

from requests.exceptions import (
    ConnectionError,
    ConnectTimeout,
    ReadTimeout,
    ChunkedEncodingError
)

from .        import exceptions as e
from .search  import Search
from .image   import Image
from .options import ParseOptions
from .utils   import (
    C,
    get_base_url,
    draw_bar,
    rewrite_text,
    hide_cursor,
    show_cursor,
    next_line,
    erase_up,
    MIMETYPE_EXT
)

ask = (
    'HIGH RESOLUTION IMAGES OF {0}',
    'IMAGES OF {0}',
    'I WANT IMAGES OF {0}',
    'DOWNLOAD IMAGES OF {0}',
    'PICTURES OF {0}'
    'FREE DOWNLOAD IMAGES OF {0}',
    'I WANT PICTURES OF {0}',
    'HIGH RESOLUTION PICTURES OF {0}',
)

def main():
    def _error(error):
        print(error, file = sys.stderr)

    me         = sys.argv[0]
    opts, args = ParseOptions()

    if len(args) == 0:
        _error("{0}: No query string(s), try `{0} -h' for more info.".format(me))
        exit(1)
    if opts.n < opts.image_count:
        _error("{0}: argument passed to `-n' must be > that of `-m'".format(me))
        exit(1)

    def _info(info, **kargs):
        print(info, file = sys.stdout, **kargs)

    tries = 0
    def _connection_handler(t = None, **kargs):
        nonlocal tries
        if kargs.get('nl'): next_line()
        t = (', ' + t) if t else ' to connect'
        if opts.retries == tries:
            _error('[{0}] Failed{1}.'.format(C('E', opts.color), t))
            show_cursor()
            exit(1)
        tries += 1
        _error('[{0}] Failed{1}.'.format(C('W', opts.color), t))

    def _interrupt_handler(**kargs):
        if kargs.get('nl'): next_line()
        _error('^Interrupted by user.')
        show_cursor()
        exit(1)

    def _in_domains(url):
        if opts.no_domains is None:
            return 0
        return len( list( filter(lambda d: url.endswith(d), re.split(',', opts.no_domains)) ) )

    hide_cursor()
    engine_index = 0
    engines      = re.split(',', opts.engine)
    search       = Search(engine = engines[0], timeout = opts.timeout, save = False)
    for query in args:
        search.set_query(random.choice(ask).format(query))

        n_failed = 0
        urls     = set()
        while True:
            try:
                urls = set(urls)
                while opts.number_sites != len(urls):
                    results = search.next()
                    urls    = urls.union(results[0:opts.number_sites - len(urls)])
                break
            except ConnectTimeout:
                _connection_handler('Connection timeout')
            except ReadTimeout:
                _connection_handler('Read timeout')
            except ConnectionError:
                _connection_handler()
            except e.HTTPResponseError:
                _error('[{0}] Could not search, HTTP response error.'.format(C('W', opts.color)))
                if len(engines) > 1 and n_failed == 5:
                    n_failed = 0
                    engine_index += 1
                    if len(engines) == engine_index:
                        engine_index = 0
                    search.set_engine(engines[engine_index])

                if opts.retries == tries:
                    if len(urls) > 0:
                        break
                    show_cursor()
                    exit(1)
                tries    += 1
                n_failed += 1
            except KeyboardInterrupt:
                _interrupt_handler()
            except e.OutOfBoundError:
                break

        urls = list(urls)
        random.shuffle(urls)

        n = 0
        for url in urls:
            if _in_domains(get_base_url(url)):
                continue

            if opts.search:
                _info(url if len(args) == 1 else '{0},{1}'.format(query, url))
                n += 1
                if opts.n == n:
                    show_cursor()
                    exit(0)
                continue

            ntries      = 0
            image_links = []
            image       = Image(url = url, subject = query, timeout = opts.timeout)

            if not opts.image_link:
                _info('[{0}] {1}'.format(C('S', opts.color), image.base_url))

            while True:
                try:
                    nb_lines = 0
                    if len(image_links) < opts.image_count:
                        for link in image.get_links(
                            opts.image_count,
                            min_score   = opts.score,
                            use_content = False if opts.score == 0 else True
                        ):
                            if image_links.count(link) != 0:
                                continue
                            if opts.verbose:
                                _info('[{0}] Found {1}'.format(C('I', opts.color), link))

                            if opts.image_link:
                                hash = { 'd': 'content', 'l': 'url', 's': 'score' }

                                def sub(m):
                                    if key := hash.get(m.group(1)):
                                        return link[key]
                                    if m.group(1) == 'e':
                                        return MIMETYPE_EXT[link['mime'].casefold()]
                                    if m.group(1) == 'w':
                                        return image.url
                                    _error("[{0}]: unrecognized format specifier `{1}'".format(C('E', opts.color), m.group(1)))
                                    exit(1)

                                _info(re.sub(r'(?<!\\)\{(e|w|l|s|d)\}', sub, opts.image_link))
                                image_links.append(link)
                                n += 1

                            while opts.image_link is None:
                                filename = None
                                try:
                                    if filename is not None:
                                        _info('[{0}] Retrying to download {1}'.format(C('I', opts.color), filename))

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
                                                length   = len(read)
                                                nb_lines = 1
                                            else:
                                                draw_bar(read.removesuffix('%'), 30)
                                                _info(read, end = '')
                                                nb_lines = 2
                                            continue

                                        filename = basename(stat['filename'])
                                        size     = stat['size']

                                        ln   = ' ' if size.startswith('0') or not opts.no_progress else '\n'
                                        _str = '[{0}]'.format(C('D', opts.color)) + ' Filename: {0}, Size: {1}'
                                        _info(_str.format(filename, size), end = ln)

                                    next_line()
                                    if nb_lines and opts.more_lines:
                                        erase_up(nb_lines + 1)

                                    n += 1
                                    image_links.append(link)
                                    break
                                except KeyboardInterrupt:
                                    _interrupt_handler(nl = True)
                                except ConnectTimeout:
                                    _connection_handler('Connection timeout', nl = True)
                                except ReadTimeout:
                                    _connection_handler('Read timeout', nl = True)
                                except ConnectionError:
                                    _connection_handler(nl = True)
                                    continue
                                except e.HTTPResponseError:
                                    next_line()
                                    _error('[{0}] HTTP error while downloading file {1}'.format(C('W', opts.color), filename))
                                    break
                            if opts.n == n:
                                show_cursor()
                                exit(1)
                            if len(image_links) == opts.image_count:
                                break
                    break
                except ChunkedEncodingError:
                    break
                except ConnectTimeout:
                    _connection_handler('Connection timeout')
                except ReadTimeout:
                    _connection_handler('Read timeout')
                except ConnectionError:
                    if ntries == opts.retries_per_sites:
                        break
                    ntries += 1
                    _connection_handler()
                except KeyboardInterrupt:
                    _interrupt_handler()
                except e.HTTPResponseError:
                    _error('[{0}] Could not follow {1} skipping ...'.format(C('E', opts.color), image.base_url))
                    break
    show_cursor()
    exit(0)
