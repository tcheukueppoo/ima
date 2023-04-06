#!/usr/bin/env python

import re, requests

from bs4 import BeautifulSoup
from bs4 import NavigableString

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
            if not re.match(action, form['action']):
                continue
            post_data['payload'] = {}

            for tag in form.contents:
                if isinstance(tag, NavigableString):
                    continue
                if submit_value and tag.get('type') == 'submit' and re.match(submit_value, tag.get('value')):
                    valid_submit = True
                    continue
                if tag.name != 'input' or tag.get('name') is None:
                    continue

                post_data['payload'][tag.get('name')] = tag.get('value')
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
    base_url    = kargs.get('base_url')

    if href_like is None and tag_content is None: return None

    def is_of_this_domain(href):
        if re.match(r'/(?!/)', href) or href.startswith(base_url): return True
        return False

    #if href_like: print("=======>", href_like['re'])
    hrefs_like = []
    for a in dom.find_all('a'):
        href = a.get('href')

        if href is None: return
        #if re.match('.*?Images\+of\+fullmetal\+alchemist', href): print("see real href: ", href)
        if href_like and re.match(href_like['re'], href):
            hrefs_like.append(href)

        content = a.string
        if tag_content and (
                content
            and re.match(tag_content, content.encode().decode())
            and is_of_this_domain(href)
        ):
            return href

    if href_like and len(hrefs_like) > 0:
        try:
            href = hrefs_like[ href_like['index'] if href_like['index'] else 0 ]
            return href if is_of_this_domain(href) else None
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

def http_x(method, session, link, **kargs):
    response = session.get(link, **kargs) if method == 'GET' else session.post(link, **kargs)

    if response.status_code == requests.codes.ok:
        return response.text
    raise Exception('HttpResponseError: HTTP Server Response Code: ', response.status_code)
