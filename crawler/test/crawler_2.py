# python lib
import re
import os

# 3rd party lib
import requests
import bs4


# return the txt format of the page

class Crawler(object):
    def __init__(self, url):
        self.url = url
        self.page_raw_text = self.get_page_raw_text()
        self.article_raw_text = self.get_article_raw_text()
        self.title = self.get_title()
        self.author = self.get_author()
        self.content = self.get_content()

    def get_page_raw_text(self):
        with requests.Session() as s:
            page = s.get(self.url)
            return page.text

    def get_article_raw_text(self):
        # convert to soup object
        soup = bs4.BeautifulSoup(self.page_raw_text, "html.parser")

        article_index = self.find_most_p("article", soup)
        return soup.find_all('article')[article_index]

    def find_most_p(self, within_target, soup_object):
        article = soup_object.find_all(within_target)
        index = []

        # within all article class, find the class with most 'p' classes
        for row in article:
            # print row.prettify()
            p = row.find_all('p')
            index.append(len(p))

        largest = max(index)
        for i, j in enumerate(index):
            if largest == index[i]:
                return i

    def get_title(self):
        # most of the time title is the content of the h1 tag.
        title = self.article_raw_text.findAll('h1')[0].get_text()
        return title

    def get_author(self):
        article = self.article_raw_text
        # use regex to find contain
        # problem is sometime it's not class = 'author'
        regex = re.compile('.*author.*')
        author = article.find_all(attrs={"class": regex})[0].get_text()
        # clean white space
        author = os.linesep.join([s for s in author.splitlines() if s])
        return author
        # ===============================

    def get_content(self):
        # 1st idea, find the div class = 'body', the find the 'p' in this class to extract content
        article = self.article_raw_text

        content_index = self.find_most_p("div", article)
        print content_index
        # print article.find_all('div')[content_index]
        try:
            div_name = article.find_all('div')[content_index]['class'][0]
            print "div_name", div_name
            raw_content = article.find_all("div", attrs={"class": div_name})
        except KeyError:
            pass

        try:
            print article.find_all('div')
            id_name = article.find_all('div')[content_index]['id'][0]
            print "id_name", id_name
            raw_content = article.find_all("div", attrs={"id": id_name})
        except KeyError:
            pass

        content = []
        for row in raw_content:
            paragraphs = row.find_all('p')
            for p in paragraphs:
                content.append(p)
        return content

    def print_content(self):
        for row in self.content:
            print row


url ='https://www.nytimes.com/interactive/2017/02/28/us/politics/in-their-choice-of-guests-trump-and-congressional-democrats-sent-dueling-messages.html?hp&action=click&pgtype=Homepage&clickSource=story-heading&module=b-lede-package-region&region=top-news&WT.nav=top-news'

article = Crawler(url)
print "url:", article.url
print "title: ", article.title
print "author: ", article.author
print article.print_content()
