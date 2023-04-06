#!/usr/bin/env python

import re, requests

from bs4 import BeautifulSoup

BASE_URL = r'^(.+?)(?<!/)/(?!/)'

def is_image(link, **kargs):
    session  = kargs.get('session', requests.session())
    response = session.head(link)
    if re.match('image/', response.headers.get('content-type', '')): return True
    return False

def give_hint(**kargs):
    page = kargs.get('page')
    if page is None: return
    dom = BeautifulSoup(page, 'html.parser')

    # Some sites(e.g Duckduckgo) requires HTTP POST to get the next/previous page
    if action := kargs.get('action'):
        valid_submit = False
        submit_value = kargs.get('submit_value')
        post_data    = {}

        for form in dom.find_all('form'):
            if not re.match(action, form['action']): continue

            post_data['payload'] = {}
            for t in form.contents:
                if t.name != 'input' or t.get('name') is None: continue
                if submit_value and (
                    t.get('type') == 'submit' and re.match(submit_value, t.get('name'))
                ):
                    valid_submit = True
                    continue
                post_data['payload'][t.get('name')] = t.get('value')

            if len( post_data['payload'].keys() ) > 0 and (
                submit_value is None or (
                    submit_value and valid_submit is True
                )
            ):
                post_data['action'] = form['action']
                break

        if len( post_data.keys() ) > 1:
            return post_data

    href_like   = kargs.get('href_like')
    tag_content = kargs.get('tag_content')

    if href_like is None and tag_content is None: return None

    #if href_like: print("=======>", href_like['re'])
    hrefs_like = []
    for a in dom.find_all('a'):
        href = a.get('href')

        if href is None: return
        #if re.match('.*?Images\+of\+fullmetal\+alchemist', href): print("see real href: ", href)
        if href_like and re.match(href_like['re'], href):
            hrefs_like.append(href)

        content = a.string
        if content and tag_content and re.match(tag_content, content.encode().decode()):
            print("first: " + href)
            return href

    if href_like and len(hrefs_like) > 0:
        #print("second: ", hrefs_like)
        try:
            return hrefs_like[href_like['index']]
        except:
            return None

def prepend_base_url(base_url, href):
    if re.match('https?', href):
        return href
    elif href.startswith('//'):
        return 'http:' + href
    elif re.match('/[^/]|#|\?', href):
        return base_url + '/' + re.match('/?(.+)', href).group(1)
    return href

def strip_base_url(url):
    if re.match('https?://', url):
        return '/' + re.sub(BASE_URL, '', url)
    return url

def get_base_url(link):
    return re.match(BASE_URL, link).group(1)

def download_file(link, **kargs):
    headers  = kargs.get('header')
    path     = kargs.get('path', '.')
    filename = kargs.get('filename')
    client   = kargs.get('client', requests)

    response = client.get(link, stream = True)
    if response.status_code != client.codes.ok:
        return False

    if filename is None:
        cd       = response.headers.get('content-disposition', '')
        matched  = re.search('attachment; filename="(.+)"', cd)
        filename = matched.group(1) if matched else re.match('(?:https?://)?.*/([^/]+)/?', link).group(1)

    with open(re.match('(.+[^/])/*$').group(1) + '/' + filename, 'wb') as fd:
        for chunk in response.iter_content(chunk_size = 128):
            fd.write(chunk)
