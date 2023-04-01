#!/usr/bin/env python

import re, requests
from bs4 import BeautifulSoup
from requests.models import RequestEncodingMixin

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
            if href is None or a.string is None: continue
            if re.match(tag_content, a.string):  return href
    return None

def prepend_base_url(base_url, href):
    if re.match('https?://', href): return href
    elif re.match('/[^/]', href):   return base_url + href
    elif re.match('//', href):      return re.sub('//', '', href)

def download_file(link, **kargs):
    headers  = kargs.get('header')
    path     = kargs.get('path', '.')
    filename = kargs.get('filename')
    client   = kargs.get('client', requests)

    response = client.get(link, stream = True)
    if response.status_code != client.codes.ok:
        raise Exception('HTTPResponseError: status code:', response.status_code)

    if filename is None:
        if matched := re.match('attachment; filename="(.+)"', response.headers.get('content-disposition', '')):
            filename = matched.group(1)
        else:
            filename = re.match('(?:https?://)?.*/([^/]+)/?', link).group(1)
    with open(re.match('(.+[^/])/*$').group(1) + '/' + filename, 'wb') as fd:
        for chunk in response.iter_content(chunk_size = 128):
            fd.write(chunk)
