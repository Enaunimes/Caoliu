#!/usr/bin/env python3
import concurrent.futures
from time import time
import sqlite3
import caoliu

url_template = 'http://t66y.com/thread0806.php?fid=7&search=&page={}'
urls = {url_template.format(i) for i in range(1, 101)}

def get_posts(url):
    print('{}  extracting post info...'.format(time()))
    page = caoliu.ForumPage(url)
    return page.posts

posts = set()

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    for new_post_list in executor.map(get_posts, urls):
        posts = posts.union(new_post_list)

conn = sqlite3.connect('caoliu.db')
# url, title, author_name, author_uid, pub_date, gilded, replies
#conn.execute('CREATE TABLE caoliu(url TEXT, title TEXT, author_name TEXT, author_uid TEXT, pub_date TEXT, gilded INTEGER, replies INTEGER)')
with conn:
    for p in posts:
        conn.execute("INSERT INTO caoliu VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (p.url, p.title, p.author_name, p.author_uid, p.pub_date, p.gilded, p.replies))
        print('{}  {}'.format(time(),p.url))
