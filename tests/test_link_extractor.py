#!/usr/bin/env python

import re
from ima.search import Search

ima = Search(query = "images of winry rockbell", engine = "duckduckgo")

while results := ima.next():
    for i in results: print(i)
