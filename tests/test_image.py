
import pytest

from ima.image import Image

def test_get_links():
    page  = open('./html/flower2.html')
    image = Image(page = page, subject = 'flower', base_url = 'www.freepik.com')
    for link in image.get_links(): print(link['url'])

test_get_links()
