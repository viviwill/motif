# python lib
import re

# 3rd party lib
import requests
import bs4


# return the txt format of the page
def get_page(page_url):
    with requests.Session() as s:
        page = s.get(page_url)
        return page.text


def get_article_index_v1(soup):
    # find all article class
    article = soup.find_all('article')
    index = []

    # within all article class, find the class with most 'p' classes
    # then that's the main article class, return its index
    for row in article:
        p = row.find_all('p')
        index.append(len(p))

    largest = max(index)
    for i, j in enumerate(index):
        if largest == index[i]:
            return i


def crawl(url):
    # use soup to load the page
    page_content = get_page(url)
    soup = bs4.BeautifulSoup(page_content, "html.parser")

    article_index = get_article_index_v1(soup)
    article = soup.find_all('article')[article_index]

    # find title
    # most of the time title is the content of the h1 tag.
    info_title = article.findAll('h1')[0].get_text()

    # ======= find author ==========
    # use regex to find contain
    # problem is sometime it's not class = 'author'
    regex = re.compile('.*author.*')
    info_author = article.find_all(attrs={"class": regex})[0].get_text()
    # ===============================

    # ======= article content ========
    # 1st idea, find the div class = 'body', the find the 'p' in this class to extract content
    # article_section = article.find_all('article')[0]
    info_content = article.find_all('p')
    # ================================

    print "Title: ", info_title
    print "Author: ", info_author
    print "Content:"
    for row in info_content:
        print row


url = 'https://plus.google.com/+RipRowan/posts/eVeouesvaVX'
crawl(url)
