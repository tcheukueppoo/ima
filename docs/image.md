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

1. **get_links**(self, n, \*kargs)

Possible key-value arguments are:

Navigate and return a generator of dictionaries describing the extracted image tags.

- min_score: A positive integer, It sets the minimum score an Image should have.
You can plug-in a custom function which computes the score of an image based on your
own policy. Ima has a default static method in the Image class which for each token in
self.subject checks if it is contained in the alt attribute of each image tag its found
and return the number of tokens that were present.

- score_with: Custom function to determine the image's score. It is going to be invoked
with two arguments, first argument is the self.subject and second is the content of the `alt`
attribute of the `img` tag.

- use_content: Tell Image object to ignore all `img` tags with no alt attributes.

Yielded dictionaries contain the following keys:

    1. url: Image url.
    2. content: if exists, contains the content of the alt attribute else `None`.
    3. score: The computed score, based on `content`.
    4. mime: Mimetype of the image.

2. **download_from**(self, link, \*\*kargs)



3. **download**(self, \*\*kargs)

Use this to iterate over images and download images.

It has the following key-value arguments



