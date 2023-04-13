#!/usr/bin/env python

from ima.image import Image

urls = (
    'https://unsplash.com',
    'https://wallpapercave.com/',
    'https://wallpaperscraft.com/',
    'https://pixabay.com/',
)

img = Image()

for url in urls:
    img.set_url(url)
    if links := img.get_links(count = 4):
        for link in links:
            print(link)
