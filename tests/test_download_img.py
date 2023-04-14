#!/usr/bin/env python

import requests
from ima.utils import download_image, generate_headers

session = requests.Session()
session.headers.update(generate_headers())

for progress in download_image(
    'https://images2.alphacoders.com/107/107200.jpg',
    session,
    rate = 100,
    path = '/home/kueppo/static',
):
    #print(progress)
    pass

for progress in download_image(
    'data:image/gif;base64,R0lGODlhEAAQAMQAAORHHOVSKudfOulrSOp3WOyDZu6QdvCchPGolfO0o/XBs/fNwfjZ0frl3/zy7////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAkAABAALAAAAAAQABAAAAVVICSOZGlCQAosJ6mu7fiyZeKqNKToQGDsM8hBADgUXoGAiqhSvp5QAnQKGIgUhwFUYLCVDFCrKUE1lBavAViFIDlTImbKC5Gm2hB0SlBCBMQiB0UjIQA7',
    session,
    path      = '/home/kueppo/static',
    mime_type = 'jpeg',
):
    pass
