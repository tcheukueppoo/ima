#!/usr/bin/env python

from ima.search import Search

ima = Search(query = "images of winry rockbell", engine = "duckduckgo")


save_path = '/home/kueppo/imgs'
while site := ima.get_nlinks(as_image = True, count = 4, trys = 2):
    site.download_image(path = save_path, count = 2, min_score = 1)
