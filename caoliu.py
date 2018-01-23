import re
import requests
from lxml import html

fake_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 '
                         'Edge/12.10240'}
caoliu_site = 'http://t66y.com/'

# TODO: superclass Page

class CaoliuPost:
    # TODO self.gilded
    def __init__(self, url, title, author_name, author_uid, pub_date):
        self.url = url
        self.title = title
        self.author_name = author_name
        self.author_uid = author_uid
        self.pub_date = pub_date
#        self.gilded = gilded
    def get_content(self):
        fake_headers = {}
        response = requests.get(self.url, header=fake_headers)
        return response.content.decode('GB18030')

class ForumPage:
    def __init__(self, url):
        response = requests.get(url, headers=fake_headers)
        self.content = response.content.decode('GB18030')
        page = html.fromstring(self.content)

        self.posts = []

        tbody = page.xpath('//tbody')[0]
        for tr in tbody:
            if tr.text_content() == '普通主題':
                seperator_index = tbody.index(tr)
        # excluding top and bottom seperator
        table_of_posts = tbody[seperator_index+1:-1]
        for tr in table_of_posts:
            title = tr[1][0][0].text_content()
            href = tr[1][0][0].get('href')
            author_name = tr[2][0].text_content()
            author_uid = re.search('(?<=uid\=)\d*$', tr[2][0].get('href'))
            if len(tr[2][1]) > 0:
                pub_date = re.search('\d\d\d\d-\d\d-\d\d', tr[2][1][0].get('title')).group()
            else:
                pub_date = tr[2][1].text_content()
            post = CaoliuPost(caoliu_site+href, title, author_name, author_uid, pub_date)
            self.posts.append(post)