import pytest

from ima.utils import download_file, give_hint

def test_give_hint_google():
    page = open('./html/google_index.html')
    link = give_hint(page = page, tag_content = 'Suivant|Next')
    assert '/search?q=images+of+spain&ei=KwEiZPWCAf67kdUPqq69oA4&start=10&sa=N' == link

def test_give_hint_duckduckgo():
    expected_post = {'action': '/html/', 'payload': {'q': 'images of spain', 's': '29', 'nextParams': '', 'v': 'l', 'o': 'json', 'dc': '30', 'api': 'd.js', 'vqd': '4-30714319225210572092660225968955472929', 'kl': 'wt-wt'}}
    page = open('./html/spain_duckduckgo.html')
    post = give_hint(page = page, action = '/html', submit_value = 'Next')
    assert post == expected_post

def test_give_hint_yahoo():
    page = open('./html/yahoo_index.html')
    link = give_hint(page = page, tag_content = '2')
    assert 'https://search.yahoo.com/search?p=images+of+naruto&b=8&pz=7&bct=0&pstart=2' == link

def test_download_file():
    download_file('http://localhost:3000/assets/image.jpg')

test_download_file()
