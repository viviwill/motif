import requests
import json
import bs4
import re
import os


url = 'http://www.latimes.com/business/technology/la-fi-tn-evan-spiegel-snapchat-future-20170302-story.html'

soup = bs4.BeautifulSoup(requests.get(url).content, "html.parser")

# find h1 and then use 'find_all_next' to find any class with 'author'
title = soup.find("h1")
print title

regex = re.compile('.*author.*')
try:
    author_raw = title.find_all_next(attrs={"class": regex})[0].get_text()
    print author_raw
except (AttributeError, IndexError):
    print "Can't find author"
    author = None

try:
    author_raw = title.find_all_next(attrs={"itemprop": regex})[0].get_text()
    print author_raw
except (AttributeError, IndexError):
    print "Can't find author"
    author = None