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
        default = 'duckduckgo',
        metavar = 'ENGINE',
        help    = 'Specify what search engine to use, possible search engines are '
                  'duckduckgo, google, and yahoo. Engine defaults to "google".'
    )
    parser.add_option(
        '-n',
        dest    = 'n',
        type    = 'int',
        default = 2,
        metavar = 'NUM',
        help    = 'Print NUM results obtained from the `-s\' or `-i\' option or when neither '
                  'of these options were specified, i.e the number of images to download.'
    )
    parser.add_option(
        '-p', '--progress',
        dest    = 'progress',
        action  = 'store_false',
        default = True,
        help    = 'Show download progress bar.'
    )
    parser.add_option(
        '-l', '--image-links',
        dest    = 'image_links',
        default = '{l}',
        metavar = 'OUTPUT_FORMAT',
        help    = 'Output image links instead of downloading them. You can use the following specifiers to format '
                  'output: `{s}\' represents the score of the given image, `{d}\' its description, and `{l}\' its '
                  'url. e.g: we can for example format our output as such "image {l} has score {s}".'
    )
    parser.add_option(
        '-s', '--search-only',
        dest    = 'search',
        action  = 'store_true',
        default = False,
        help    = 'Query search engine and output search result only. This option is in conflict '
                  'with the `-l\' option.'
    )
    parser.add_option(
        '-m', '--image-count',
        dest    = 'image_count',
        type    = 'int',
        default = 5,
        metavar = 'NUM',
        help    = 'Set NUM as maximum number of image links to be extracted on a website obtained from search results.'
    )
    parser.add_option(
        '-d', '--dest-dir',
        dest    = 'dest_dir',
        type    = 'string',
        default = '.',
        metavar = 'DEST_DIR',
        help    = 'Specify the destination directory were downloaded files should be stored, '
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
        '-r', '--retrys',
        dest    = 'retrys',
        type    = 'int',
        default = 2,
        metavar = 'NUM',
        help    = 'Number of retrys if the first connection to any of the websites obtained '
                  'from search results fails. A negative number implies infinity.'
    )
    parser.add_option(
        '-i', '--ignore-domain',
        dest    = 'no_domain',
        type    = 'string',
        default = None,
        metavar = 'DOMAIN',
        help    = 'A comma separated list of domains to ignore on search results.'
    )
    parser.add_option(
        '-w', '--overwrite',
        dest    = 'overwrite',
        action  = 'store_true',
        type    = 'int',
        default = False,
        help    = 'Overwrite existing files'
    )

    opts, args = parser.parse_args(sys.argv[1:])
    return opts, args
