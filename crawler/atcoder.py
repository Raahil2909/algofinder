import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
import os
from os.path import join, dirname
from pymongo import MongoClient
import sys
from urllib.parse import urlparse, urljoin
sys.path.append(f'../{os.getcwd()}')
parlink = 'https://atcoder.jp/contests/archive?page='
dom = 'https://atcoder.jp/'
# we need to append numbers to link and then find all the links on the page and visit them
load_dotenv()
cnxn = os.environ.get('CNXN')
db = MongoClient(cnxn).algofinder
atLinksTable = db.atlinks
atLinksTable.create_index('link', unique=True)

userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
session = requests.session()


def crawler():
    links = []
    for i in range(1, 10):
        curlink = parlink + str(i)
        resp = session.get(curlink)
        soup = BeautifulSoup(resp.content, "html.parser")
        for link in soup.find_all("a"):
            url = urlparse(link.get("href")).path
            if 'bytes' in str(type(url)):
                continue
            # if '/contents/abc' in url or '/contests/arc' in url or '/contests/agc' in url or '/contests/ahc' in url:
            if re.findall('/contests/a[bgr]c\d+', url):
                if url[-1] != '/':
                    url += '/'
                finallink = urljoin(urljoin(dom, url), 'tasks/')
                resp = session.get(finallink)
                soup = BeautifulSoup(resp.content, "html.parser")
                for link in soup.find_all("a"):
                    url = urlparse(link.get("href")).path
                    if url == b'':
                        continue
                    if re.findall('.*/tasks/a[bgr]c.*', url):
                        links.append({"domain": "atcoder.jp", "link": url})
    print(links)
    try:
        atLinksTable.insert_many(links, ordered=False)
    except Exception as E:
        print(E)


if __name__ == '__main__':
    crawler()
