# IMA

## Image in ima.image

### Image(\*kargs)

Create a new Image object. key-value arguments are:

- url: url from which image links are going to be extracted.
- subject: Set space separated list of token use for scoring an extracted images.
- timeout: Connection Timeout, default value is 10 seconds.

### Methods

#### Accessors

**set_url**(self, string)

Set url from which image links are going to be extracted.

#### Class Method

1. **get_links**(self, n, \*kargs)

Possible key-value arguments are:

- save: A boolean, set to `True` to cache search results.

- start: Tell search object to extract links as from the start of the page if `start`
is True, otherwise just extract by continuing from the current page.

- as\_image: Set to True to return a generator of `Image` of objects.

- score: for which their existence would
be checked in the alt attribute of the image tag. This can be useful to obtain
quality results.

Navigate and get `n` links as a list of urls if `as_image` is `False` otherwise return
a list of image objects.

2. **download_from**(self, as\_image = `Boolean`, save = `Boolean`)



3. **download**(self, as\_image = `Boolean`, save = `Boolean`)

Navigate to the previous page and return the result as a list of urls if `as_image`
is False otherwise, return a generator of `Image` objects.


