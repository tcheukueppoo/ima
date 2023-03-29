#!/usr/bin/env python

import re, requests
from bs4 import BeautifulSoup

def goto(**kargs):
    form_index   = kargs.get('form_index', 1)
    submit_value = kargs.get('submit_value', '')
    tag_regex    = kargs.get('content_like')
    content      = kargs.get('content')

    if content is None: return

    dom = BeautifulSoup(content, 'html.parser')
    if tag_regex is not None:
        for a in dom.find_all('a'):
            href = a.get('href')
            if re.match(tag_regex, a.stripped_string):
                return href
    elif form_index is not None or submit_value is not None:
        index        = 0
        post_data    = {}
        valid_submit = False
        for form in dom.find_all('form'):
            index += 1
            post_data = {}
            if index < form_index: continue
            for input in form.contents:
                if input['type'] == 'submit' and re.match(submit_value, input['name']):
                    valid_submit = True
                if input.name == 'input' and input['type'] != 'submit':
                    post_data[input['name']] = input['value']
            if valid_submit is True: break
        return post_data
    return None
