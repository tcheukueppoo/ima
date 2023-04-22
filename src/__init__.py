import sys
import random

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
    me = sys.argv[0]

    opts, args = ParseOptions()

    LOG['ERR']  = open(opts.log_file, 'a') if opts.log_file else sys.stderr
    LOG['WARN'] = log_err
    LOG['INFO'] = log_err if opts.log_file else sys.stdout

    def _log(type, message):
        print('[{0}]: {1}'.format(type, message), file = LOG[type])
        if type == 'ERR': exit(1)

    search = Search(engine = opts.engine, save = False)
    if len(args) == 0:
        _log('ERR', "{0}: No query string, try `{0} --help' for more info".format(me))

    for query in args:
        search.set_engine(query)

        trys, count = 0, 0
        try:
            for link in search.next():
                count += 1
                if opts.search:
                    pass
        except exceptions.HTTPResponseError:
            pass
        except ConnectionError:
            pass
    
