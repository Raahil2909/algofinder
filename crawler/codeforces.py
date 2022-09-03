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
parlink = 'https://codeforces.com/problemset/page/'
# we need to append numbers to link and then find all the links on the page and visit them
load_dotenv()
cnxn = os.environ.get('CNXN')
db = MongoClient(cnxn).algofinder
cfLinksTable = db.cflinks
cfLinksTable.create_index('link', unique=True)

userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
session = requests.session()


def crawler():
    links = []
    for i in range(1, 82):
        curlink = parlink + str(i)
        resp = session.get(curlink)
        soup = BeautifulSoup(resp.content, "html.parser")
        for link in soup.find_all("a"):
            url = urlparse(link.get("href")).path
            if 'problemset/problem' in url:
                links.append({"domain": "codeforces.com", "link": url})
    try:
        cfLinksTable.insert_many(links, ordered=False)
    except Exception as E:
        print(E)


if __name__ == '__main__':
    crawler()
