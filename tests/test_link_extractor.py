#!/usr/bin/env python

from ima.search import Search

ima = Search(query = "images of winry rockbell", engine = "duckduckgo")

# with DuckDuckGO
"""
while results := ima.next():
    for link in results: print(link)
"""

# now with Google!
i = 1
ima.set_engine('yahoo').set_query('Edward Elric')
while results := ima.next():
    if i == 2:
        results = ima.back()
        break
    for link in results: print(link)
    i += 1
