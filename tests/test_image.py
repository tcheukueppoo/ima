
import pytest, requests

from ima.image import Image

def test_get_links():
    page  = open('./html/flower2.html')
    image = Image(page = page, subject = 'flower', base_url = 'www.freepik.com')
    for link in image.get_links(): print(link['url'])

def test_download_image():
    session = requests.Session()
    response = session.get('http://localhost:5042/en-US/docs/Web/HTTP/CORS')
    image = Image(page = response.text, base_url = 'http://localhost:5042')
    for link in image.get_links(): print(link)

test_download_image()
