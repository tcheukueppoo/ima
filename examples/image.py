#!/usr/bin/env python

from ima.image import Image

img  = Image()
urls = (
    'https://unsplash.com',
    'https://wallpapercave.com/',
    'https://wallpaperscraft.com/',
    'https://pixabay.com/',
)

for url in urls:
    img.set_url(url)
    links = img.get_links(count = 4):
    if not links: continue
    for link in links:
        print(link)
