#!/usr/bin/env python3
import re
from time import time
import concurrent.futures
import caoliu

FORUM_URL = "http://t66y.com/thread0806.php?fid=25"

guochan_forum = caoliu.ForumPage(FORUM_URL)

post_urls = [post.url for post in guochan_forum.posts if re.search('fhd', post.title, re.I)]

print('Parsing posts to find torrents...')
torrent_urls = set()
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    for url in post_urls:
        futures = {executor.submit(caoliu.grab_torrent_url, url) for url in post_urls}
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as exc:
                print('ERR: %s' % exc)
            else:
                torrent_urls.add(result)
                print('parsing...')
                
if None in torrent_urls:
    torrent_urls.remove(None)

print('Downloading torrents')
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(caoliu.download_torrent, url) for url in torrent_urls}
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as exc:
            print('Failed %s' % exc)
        else:
            print('Done')
