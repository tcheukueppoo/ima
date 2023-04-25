import sys
import random
import re
import ansi.cursor as c

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
    next_line
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
    def _connection_handler(t = None, **kargs):
        nonlocal trys
        if kargs.get('nl'): next_line()
        t = (', ' + t) if t else ' to connect'
        if opts.retrys == trys:
            _error('[{0}] Failed{1}.'.format(C('E', opts.color), t))
            show_cursor()
            exit(1)
        trys += 1
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
    search = Search(engine = opts.engine, timeout = opts.timeout, save = False)
    for query in args:
        search.set_query(random.choice(ask).format(query))

        n       = 0
        n_sites = 0
        while True:
            try:
                if n_sites == opts.number_sites:
                    show_cursor()
                    exit(1)
                results = search.next()
                indexes = range(0, len(results))
                for i in indexes:
                    c = random.choice(list(indexes))
                    results[i], results[c] = results[c], results[i]

                if opts.search:
                    for url in results:
                        if _in_domains(get_base_url(url)): continue
                        _info(url if len(args) == 1 else '{0},{1}'.format(query, url))
                        n += 1
                        if opts.n == n:
                            show_cursor()
                            exit(0)
                    continue

                valid_site = False
                for u in results:
                    image = Image(url = u, subject = query, timeout = opts.timeout)
                    if _in_domains(image.base_url):
                        continue

                    _info('[{0}] {1}'.format(C('S', opts.color), image.base_url))

                    image_links   = []
                    ntrys = 0
                    while True:
                        try:
                            if ntrys == opts.retrys_per_sites:
                                break
                            if len(image_links) < opts.image_count:
                                for link in image.get_links(
                                    opts.image_count,
                                    min_score   = opts.score,
                                    use_content = False if opts.score == 0 else True
                                ):
                                    if not valid_site: valid_site = True
                                    if image_links.count(link) != 0:
                                        continue
                                    if opts.verbose:
                                        _info('[{0}] Found {1}'.format(C('I', opts.color), link))

                                    if opts.image_link:
                                        hash = { 'd': 'content', 'l': 'url', 's': 'score' }
                                        _info(re.sub(r'(?<!\\)\{(l|s|d)\}', lambda m: link[hash[m.group(1)]], opts.image_link))
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
                                                        length = len(read)
                                                    else:
                                                        draw_bar(read.removesuffix('%'), 30)
                                                        _info(read, end = '')
                                                    continue

                                                filename = basename(stat['filename'])
                                                size     = stat['size']

                                                ln   = ' ' if size.startswith('0') or not opts.no_progress else '\n'
                                                _str = '[{0}]'.format(C('D', opts.color)) + ' Filename: {0}, Size: {1}'
                                                _info(_str.format(filename, size), end = ln)

                                            next_line()
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
                            ntrys += 1
                            _connection_handler()
                        except KeyboardInterrupt:
                            _interrupt_handler()
                        except e.HTTPResponseError:
                            _error('[{0}] Could not follow {1} skipping ...'.format(C('E', opts.color), image.base_url))
                            break

                    if valid_site:
                        n_sites += 1
            except ConnectTimeout:
                _connection_handler('Connection timeout')
            except ReadTimeout:
                _connection_handler('Read timeout')
            except ConnectionError:
                _connection_handler()
            except e.HTTPResponseError:
                _error('[{0}] Could not search, HTTP response error.'.format(C('W', opts.color)))
                if opts.retrys == trys:
                    show_cursor()
                    exit(1)
                trys += 1
            except KeyboardInterrupt:
                _interrupt_handler()
            except e.OutOfBoundError:
                show_cursor()
                exit(0)

