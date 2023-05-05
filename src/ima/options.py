import sys
import optparse

from shutil   import get_terminal_size
from .version import __version__

def format_option(option):
    opts = []

    if option._short_opts:
        opts.append(option._short_opts[0])
    if option._long_opts:
        opts.append(option._long_opts[0])
    if len(opts) > 1:
        opts.insert(1, ', ')
    if option.takes_value():
        opts.append(' %s' % option.metavar)

    return ''.join(opts)

def ParseOptions():
    columns   = get_terminal_size().columns
    max_width = columns if columns else 80
    fmt       = optparse.IndentedHelpFormatter(width = max_width, max_help_position = 80)

    fmt.format_option_strings = format_option

    kwargs = {
        'version': __version__,
        'formatter': fmt,
        'usage': '%prog [OPTIONS] QUERY [QUERY...]',
        'conflict_handler': 'resolve',
    }

    parser = optparse.OptionParser(**kwargs)
    parser.add_option(
        '--version',
        action = 'version',
        help   = 'Print program version and exit.'
    )
    parser.add_option(
        '-h', '--help',
        action = 'help',
        help   = 'Print this help text and exit.'
    )
    parser.add_option(
        '-v', '--verbose',
        dest    = 'verbose',
        action  = 'store_true',
        default = False,
        help    = 'Print status messages to the standard output.'
    )
    parser.add_option(
        '-e', '--engine',
        dest    = 'engine',
        default = 'google',
        metavar = 'ENGINE',
        help    = 'Comma separated list of search engines to use, possible search engines are '
                  'duckduckgo, google, and yahoo. Engine defaults to "google". If more than '
                  'one search engine is specified, cycle through when connection fails too much.'
    )
    parser.add_option(
        '-n',
        dest    = 'n',
        type    = 'int',
        default = 4,
        metavar = 'NUM',
        help    = 'Print NUM results obtained from the `-s\' or `-i\' option or download NUM images '
                  'when neither of these options were specified.'
    )
    parser.add_option(
        '-u', '--number-sites',
        dest    = 'number_sites',
        type    = 'int',
        default = 10,
        metavar = 'NUM',
        help    = 'The number of websites to visit.'
    )
    parser.add_option(
        '-p', '--no-progress-bar',
        dest    = 'no_progress',
        action  = 'store_false',
        default = True,
        help    = 'Disable progress bar for downloads.'
    )
    parser.add_option(
        '-l', '--image-link',
        dest    = 'image_link',
        default = None,
        metavar = 'OUTPUT_FORMAT',
        help    = 'Output image links instead of downloading them. You can use the following specifiers to format '
                  'output: `{s}\' represents the score of the given image, `{d}\' its description, `{l}\' its '
                  'url, `{e}\' its file extension and `{w}\' the url from which the image link was extracted '
                  'e.g: we can for example format our output as such --> "image {l} has score {s}".'
    )
    parser.add_option(
        '-s', '--search-only',
        dest    = 'search',
        action  = 'store_true',
        default = False,
        help    = 'Query search engine and output search results only. This option is in conflict '
                  'with the `-l\' option.'
    )
    parser.add_option(
        '-m', '--image-count',
        dest    = 'image_count',
        type    = 'int',
        default = 2,
        metavar = 'NUM',
        help    = 'Set NUM as maximum number of image links to be extracted from a website.'
    )
    parser.add_option(
        '-d', '--dest-dir',
        dest    = 'dest_dir',
        type    = 'string',
        default = '.',
        metavar = 'DEST_DIR',
        help    = 'Specify the destination directory were downloaded files will be stored, '
                  'default to the current working directory of the executing program.'
    )
    parser.add_option(
        '-o', '--min-score',
        dest    = 'score',
        type    = 'int',
        default = 0,
        metavar = 'SCORE',
        help    = 'Define mininum score for images. This option should not be used with the `-s\' option.'
    )
    parser.add_option(
        '-r', '--retries',
        dest    = 'retries',
        type    = 'int',
        default = 0,
        metavar = 'NUM',
        help    = 'Number of retries before giving up if any connection fails.'
    )
    parser.add_option(
        '-x', '--retries-per-sites',
        dest    = 'retries_per_sites',
        type    = 'int',
        default = 0,
        metavar = 'NUM',
        help    = 'Number of retries per sites if any connection fails.'
    )
    parser.add_option(
        '-i', '--ignore-domains',
        dest    = 'no_domains',
        type    = 'string',
        default = None,
        metavar = 'DOMAIN',
        help    = 'A comma separated list of domains to ignore on search results.'
    )
    parser.add_option(
        '-w', '--overwrite',
        dest    = 'overwrite',
        action  = 'store_true',
        default = False,
        help    = 'Overwrite existing files, This option is in conflict with the `-a\' option.'
    )
    parser.add_option(
        '-a', '--auto-name',
        dest    = 'auto',
        action  = 'store_true',
        default = False,
        help    = 'Auto generate a new file name if a file name already exist in filesystem.'
    )
    parser.add_option(
        '-k', '--no-color',
        dest    = 'color',
        action  = 'store_false',
        default = True,
        help    = 'Disable ANSI colors'
    )
    parser.add_option(
        '-t', '--timeout',
        dest    = 'timeout',
        metavar = 'TIMEOUT',
        type    = 'int',
        default = 10,
        help    = 'Set connection timeout.'
    )
    parser.add_option(
        '-q', '--less-lines',
        dest    = 'more_lines',
        action  = 'store_true',
        default = False,
        help    = 'Wipe download progress bar after download has finished'
    )

    opts, args = parser.parse_args(sys.argv[1:])
    return opts, args
