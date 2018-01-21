#!/usr/bin/env python3
import re
import requests
from time import sleep
from lxml import html

fake_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

def get_post_urls():
    caoliu_address = 'http://t66y.com/thread0806.php?fid=25'
    response = requests.get(caoliu_address, headers=fake_headers)
    page = html.fromstring(response.content)
    url_match = re.compile('^htm_data/\d*/\d*/\d*\.html$')
    page_urls = set()
    for anchor in page.xpath('//a[@href]'):
        if url_match.match(anchor.get('href')):
            page_urls.add('http://t66y.com/{}'.format(anchor.get('href')))
    return list(page_urls)

def get_rmdown_fake_url(post_url):
    response = requests.get(post_url, headers=fake_headers)
    page = html.fromstring(response.content)
    rmdown_match = re.compile('^http\://www\.rmdown\.com/link\.php\?hash\=[a-z0-9]*$')
    for anchor in page.xpath('//a'):
        if rmdown_match.match(anchor.text_content()):
            return anchor.text_content()

def get_rmdown_real_url(url):
    response = requests.get(url, headers=fake_headers)
    page = html.fromstring(response.content)
    form = page.xpath('//form')[0]
    reff = form.xpath('input[@name="reff"]')[0].get('value')
    ref = form.xpath('input[@name="ref"]')[0].get('value')
    real_url = 'http://www.rmdown.com/download.php?reff={}&ref={}'.format(reff, ref)
    return real_url

def download_torrent(url):
    filename = '{}.torrent'.format(re.search('(?<=ref\=)[0-9a-z]*$', url).group())
    response = requests.get(url, headers=fake_headers)
    with open(filename, 'bw') as torrent_file:
        torrent_file.write(response.content)

if __name__ == '__main__':
    for url in get_post_urls():
        fake_url = get_rmdown_fake_url(url)
        if fake_url:
            real_url = get_rmdown_real_url(fake_url)
        print(real_url)
        if real_url:
            try:
                download_torrent(real_url)
                print('Done {}'.format(real_url))
            except:
                sleep(1)
                download_torrent(real_url)
                print('Done {}'.format(real_url))
