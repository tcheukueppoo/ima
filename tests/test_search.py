#!/usr/bin/env python

import pytest
from ima.search import Search

search = Search(engine = 'google', query = 'images of madara')

def test_url_operations():
    assert search.set_engine('duckduckgo').url                == 'https://duckduckgo.com/html/?q=images+of+naruto'
    assert search.set_query('naruto').set_engine('yahoo').url == 'https://search.yahoo.com/search/?p=naruto'

def test_extract_links():
    html = open('./html/google_index.html')
    search.page = html
    links = search.next()
    search.set_engine('duckduckgo')
    html = open('./html/spain_duckduckgo.html')
    search.page = html
    links += search.next()
    html = open('./html/yahoo_index.html')
    search.page = html
    search.set_engine('yahoo')
    links += search.next()
    #assert len(links) == len(expected_links)
    #assert all([ links == expected_links for a, b in zip(links, expected_links) ])

def test_next():
    for link in search.next(): print(link)
