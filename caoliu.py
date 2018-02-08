import re
import requests
from lxml import html

fake_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 '
                         'Edge/12.10240'}
caoliu_site = 'http://t66y.com/'

# TODO: superclass Page

class CaoliuPost:
    # TODO change positional arguments to keyword arguments
    def __init__(self, url, title, author_name, author_uid, pub_date, gilded):
        self.url = url
        self.title = title
        self.author_name = author_name
        self.author_uid = author_uid
        self.pub_date = pub_date
        self.gilded = gilded
    def get_content(self):
        fake_headers = {}
        response = requests.get(self.url, headers=fake_headers)
        return response.content.decode('GB18030')

class ForumPage:
    def __init__(self, url):
        response = requests.get(url, headers=fake_headers)
        self.content = response.content.decode('GB18030')
        page = html.fromstring(self.content)

        self.posts = []

        tbody = page.xpath('//tbody')[-1]
        for tr in tbody:
            if tr.text_content() == '普通主題':
                seperator_index = tbody.index(tr)
                # excluding top and bottom seperator
                table_of_posts = tbody[seperator_index+1:-1]
                break
        else:
            table_of_posts = tbody[2:-1]
        for tr in table_of_posts:
            title = tr[1][0][0].text_content()
            href = tr[1][0][0].get('href')
            author_name = tr[2][0].text_content()
            author_uid = re.search('(?<=uid\=)\d*$', tr[2][0].get('href'))
            if len(tr[2][1]) > 0:
                pub_date = re.search('\d\d\d\d-\d\d-\d\d', tr[2][1][0].get('title')).group()
            else:
                pub_date = tr[2][1].text_content()
            if tr.xpath('.//span[@class="sgreen"]'):
                gilded = True
            else:
                gilded = False
            post = CaoliuPost(caoliu_site+href, title, author_name, author_uid, pub_date, gilded)
            self.posts.append(post)

def grab_torrent_url(post):
    page = html.fromstring(post.get_content())
    rmdown_match = re.compile('^http\://www\.rmdown\.com/link\.php\?hash\=[a-z0-9]*$')
    for anchor in page.xpath('//a'):
        if rmdown_match.match(anchor.text_content()):
            dl_page_url = anchor.text_content()
            response = requests.get(dl_page_url, headers=fake_headers)
            page = html.fromstring(response.content)
            form = page.xpath('//form')[0]
            reff = form.xpath('input[@name="reff"]')[0].get('value')
            ref = form.xpath('input[@name="ref"]')[0].get('value')
            return 'http://www.rmdown.com/download.php?reff={}&ref={}'.format(reff, ref)
    else:
        return None

def download_torrent(torrent_url, filename=None):
    try:
        filename = '{}.torrent'.format(re.search('(?<=ref\=)[a-z0-9]*$', torrent_url).group())
    except AttributeError:
        return None
    else:
        response = requests.get(torrent_url, headers=fake_headers)
        with open(filename, 'bw') as file_output:
            file_output.write(response.content)
        return None
