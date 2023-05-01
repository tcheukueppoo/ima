# IMA

## Image in ima.image

### Image(\*kargs)

Create a new Image object. key-value arguments are:

- url: Url from which image links are going to be extracted.
- subject: Set space separated list of token use for scoring an extracted images.
- timeout: Connection Timeout, default value is 10 seconds.

### Methods

#### Accessors

**set_url**(self, string)

Set url from which image links are going to be extracted.

#### Class Method

1. **get_links**(self, n, \*\*kargs)

Possible key-value arguments are:

Navigate and return a generator of dictionaries describing the extracted image tags.

- **min_score**: A positive integer, it is the minimum score an Image should have.
You can plug-in a custom function which computes the score of an image based on your
own policy. Ima has a default static method in the `Image` class, it does the following:
for each token in self.subject it checks if it is contained in the alt attribute of each
image tag its found and return the number of tokens that were present.

- **score_with**: Custom function to determine the image's score. It is going to be
invoked with two arguments, first argument is the self.subject and second is the
content of the `alt` attribute of the `img` tag.

- **use_content**: Tell Image object to ignore all `img` tags with no alt attributes.

Yielded dictionaries contain the following keys:

    1. url: Image url.
    2. content: if exists, contains the content of the alt attribute else `None`.
    3. score: The computed score, based on `content`.
    4. mime: Mimetype of the image.

2. **download_from**(self, link, \*\*kargs)

link can either be a url or a dict of the type of the one yield by `self.get_links(...)`.

It has the following optional key-value arguments:

- **filename**: Preferred name of the image to be download.
- 

3. **download**(self, \*\*kargs)

Use this to iterate over images and download them.

It has the following optional key-value arguments:

- rate: Download rate, set the number of bytes to retrieve per iteration.
- overwrite: Set to `True` to overwrite files that already exist.
- path: Path to the downloaded images
- auto: Set to `True` to auto generate a new name if another file with the same as the file
to be downloaded already exist in filesystem.
