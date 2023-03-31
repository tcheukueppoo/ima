#!/usr/bin/env python

import re
from bs4 import BeautifulSoup

def give_hint(**kargs):
    action       = kargs.get('action')
    tag_content  = kargs.get('tag_content')
    page         = kargs.get('page')
    submit_value = kargs.get('submit_value')

    if page is None: return
    dom = BeautifulSoup(page, 'html.parser')
    if action is not None:
        index        = 0
        post_data    = {}
        valid_submit = False

        for form in dom.find_all('form'):
            index += 1
            if not re.match(action, form['action']): continue
            post_data['action']  = form['action']
            post_data['payload'] = {}
            if submit_value is None: valid_submit = True
            for input in form.contents:
                if input.name != 'input' or input.get('name') is None: continue
                if submit_value is not None and input.get('type') == 'submit' and re.match(submit_value, input.get('name')):
                    valid_submit = True
                    continue
                post_data['payload'][input.get('name')] = input.get('value')
            if valid_submit is True: break
        return post_data
    elif tag_content is not None:
        for a in dom.find_all('a'):
            href = a.get('href')
            if href is None or a.string is None:
                continue
            if re.match(tag_content, a.string):
                return href
    return None

def prepend_base_url(base_url, href):
    if re.match('https?://', href):
        return href
    elif re.match('/[^/]', href):
        return base_url + href
    elif re.match('//', href):
        return re.sub('//', '', href)
