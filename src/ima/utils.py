#!/usr/bin/env python

import re, requests
from bs4 import BeautifulSoup
from requests.models import RequestEncodingMixin

def give_hint(**kargs):
    page = kargs.get('page')
    if page is None: return None

    dom = BeautifulSoup(page, 'html.parser')
    if action := kargs.get('action'):
        valid_submit = False
        submit_value = kargs.get('submit_value')
        form_count   = 0
        post_data    = {}
        for form in dom.find_all('form'):
            form_count += 1
            if not re.match(action, form['action']):
                continue
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

    if next_to := kargs.get('next_to'):
        pass

    href_like   = kargs.get('href_like')
    tag_content = kargs.get('tag_content')
    if href_like is None and tag_content is None:
        return None
    for a in dom.find_all('a'):
        href = a.get('href')
        if href_like and re.match(href_like, href):
            return href
        if tag_content and re.match(tag_content, a.string):
            return href


def prepend_base_url(base_url, href):
    if re.match('https?', href):
        return href
    elif re.match('//', href):
        return re.sub('//', '', href)
    elif re.match('/[^/]|#|\?', href):
        return base_url + '/' + re.match('/?(.+)', href).group(1)

def get_base_url(link):
    return re.match(r'(.+?)(?<!/)/(?!/)', link).group(1)

def download_file(link, **kargs):
    headers  = kargs.get('header')
    path     = kargs.get('path', '.')
    filename = kargs.get('filename')
    client   = kargs.get('client', requests)

    response = client.get(link, stream = True)
    if response.status_code != client.codes.ok:
        return False

    if filename is None:
        if matched := re.match('attachment; filename="(.+)"', response.headers.get('content-disposition', '')):
            filename = matched.group(1)
        else:
            filename = re.match('(?:https?://)?.*/([^/]+)/?', link).group(1)
    with open(re.match('(.+[^/])/*$').group(1) + '/' + filename, 'wb') as fd:
        for chunk in response.iter_content(chunk_size = 128):
            fd.write(chunk)
