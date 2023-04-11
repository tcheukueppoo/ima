#!/usr/bin/env python

from ima.image import Image

urls = (
    'https://pixabay.com/',
    'https://wallpapercave.com/',
    'https://wallpaperscraft.com/',
)

img = Image()

for url in urls:
    img.set_url(url)
    links = img.get_links(count = 4)
    if links:
        for link in links:
            print(link)
