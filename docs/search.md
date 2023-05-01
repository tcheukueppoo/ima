# IMA

IMA constitute of two primary classes that performs the biggest job, these
classes are Search and Image in ima.search and ima.image respectively.

## Search in ima.search

### Search(\*kargs)

Create a new search object. Arguments are:

- `engine`: Possible search engines are 'google', 'duckduckgo', and 'yahoo'.
- `query`: Your search query
- `save`: Boolean value, if set to `True`, then search results are caches
- `save_path`: Path to the directory that will contain the cache results, Defaults to your $HOME
directory.
- `timeout`: Connection Timeout, default value is 10(in seconds)

### Methods

#### Accessors

1. **set_engine**(self, string)

Set a new engine, this changes url used to make the HTTP request.

2. **set_query**(self, string)

Change query, this also changes the url used to make the HTTP request.

#### Class Method

1. **next**(self, as\_image = `Boolean`, save = `Boolean`)

Navigate to the next page and return the result as a list of urls if `as_image`
is False otherwise, return a generator of `Image` objects.

2. **back**(self, as\_image = `Boolean`, save = `Boolean`)

Navigate to the previous page and return the result as a list of urls if `as_image`
is False otherwise, return a generator of `Image` objects.

3. **get_links**(self, n, \*kargs)

Possible key-value arguments are:

- save: A boolean, set to `True` to cache search results.
- start: Tell search object to extract links as from the start of the page if `start`
is True, otherwise just extract by continuing from the current page.
- as\_image: Set to True to return a generator of `Image` of objects.

Navigate and get `n` links as a list of urls if `as_image` is `False` otherwise return
a list of image objects.

3. **query_saves**(self, \*kargs)

Possible key-value arguments are:

- query: select cached search results whose query is exactly the value set to `query`
- query\_like: select cached search results whose query matches the regular expression
set to `query_like`
- frequency: The frequency determines how many times results were cached.
So, use this parameter to select records whose frequency is the value in `frequency`.
