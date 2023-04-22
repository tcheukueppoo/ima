import optparse
from shutil import get_terminal_size

def format_option(option):
    opts = []

    if option._short_opts:
        opts.append(option._short_opts[0])
    if option._long_opts:
        opts.append(option._long_opts[0])
    if len(opts) > 1:
        opts.insert(1, ', ')
    if option.take_values():
        opts.append(' %s' % option.metavar)
    return ''.join(opts)

def ParseOption():
    columns                   = get_terminal_size()
    max_width                 = columns if columns else 80
    fmt                       = optparse.IndentedHelpFormatter(width = max_width, max_help_position = 80)
    fmt.format_option_strings = format_option

    kw = {
        'version': __version__,
        'formatter': fmt,
        'usage': '%prog [OPTIONS] QUERY [QUERY...]',
        'conflict_handler': 'resolve',
    }

    parser = optparse.OptionParser(**kw)
    parser.add_option(
        '-e', '--engine',
        dest    = 'engine',
        default = 'duckduckgo',
        help    = 'Specify what search engine to use, possible search engines are'
                  'duckduckgo, google, and yahoo.'
    )
    parser.add_option(
        '-c', '--count',
        dest    = 'count',
        default = 2,
        metavar = 'NUM'
        help    = 'Indicate the number of results to obtian from -s or -i option'
                  'or when neither of these options were specified.'
    )
    parser.add_option(
        '-sc', '--search-result-count',
        dest    = 'search_count',
        default = 5,
        metavar = 'NUM',
        help    = ''
    )
    parser.add_option(
        '-s', '--search-result',
        dest    = 'search',
        action  = 'store_true'
        default = False,
        help    = 'Query search engine and output search result only.'
    )
    parser.add_option(
        '-l', '--image-links',
        dest    = 'image',
        default = '{l}',
        metavar = 'OUTPUT_FORMAT'
        help    = 'Output image links instead of downloading, `{s}\', `{d}\', and `{l}\' represent the score,
                   image description, and image link respectively, Therefore we can for example format our output
                   as such "image {l} has score {s}".'
    )
    parser.add_option(
        '-p', '--progress',
        dest    = 'progress',
        action  = 'store_false',
        default = True,
        help    = 'Show download progress bar'
    )
    parser.add_option(
        '-v', '--verbose',
        dest    = 'verbose',
        action  = 'store_true',
        default = False,
        help    = 'Print status messages to the standard output.'
    )
    parser.add_option(
        '-d', '--destination-dir',
        dest    = 'dest_dir',
        default = '.',
        help    = 'Specify the destination directory to store the downloaded files,
                   default to the current directory of the executing program.'
    )
    parser.add_option(
        '-sc', '--score',
        dest    = 'score',
        default = 0,
        help    = 'Select '
    )
    parser.add_option(
        '-r', 'retrys',
        dest    = 'retry'
        default = 2,
        help    = 'Number of retrys if connection to any of the websites
                   from the search result fails. A negative number implies infinity '
    )
    parser.add_option(
        '-i', '--ignore-domain',
        dest    = 'no_domain',
        default = None,
        help    = 'List of domains to ignore on search results obtain from the specified search engine'
    )
