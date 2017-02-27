# from __future__ import unicode_literals
import requests
import json
import bs4

import re
import os
from datetime import datetime



class Crawler(object):
    def __init__(self, target_url):
        self.web_url = target_url
        self.title = None
        self.author = None
        self.body_content_list = None
        self.body_content_string = None
        self.pub_date = None
        self.add_date = None
        self.word_count = None
        self.domain = None
        self.crawl()

    def crawl(self):
        mercury_url = 'https://mercury.postlight.com/parser?url='
        headers = {'Content-Type': 'application/json',
                   'x-api-key': 'j9hFQ5cT1k6AwN0CshVi7RVvj2kCnCqNxoj70Evt'}
        url = mercury_url + self.web_url

        # request
        r = requests.get(url, headers=headers).content
        article = json.loads(r)

        # clean up time format
        if article['date_published'] is not None:
            self.pub_date = datetime.strptime(article['date_published'], "%Y-%m-%dT%H:%M:%S.000Z")
        self.add_date = datetime.now().replace(microsecond=0)
        self.word_count = article['word_count']
        self.domain = article['domain']

        # get title, content, and author
        self.title = article['title']
        self.parse_content(article['content'])
        # self.get_author()

    def parse_content(self, content):
        soup = bs4.BeautifulSoup(content, "html.parser")
        # print soup.prettify()
        raw_content = soup.find_all('p')

        temp_content = []
        # clean up <p class> and <a class>
        for p in raw_content:
            p = re.sub(r'<p(.*?)>', "<p class=\"article-body-content\">", str(p))
            p = re.sub(r'<a(.*?)href', "<a class=\"article-body-href\" href", str(p))
            temp_content.append(p)
        self.body_content_list = temp_content
        # self.body_content_string = unicode('\n'.join(temp_content), 'utf-8')
        self.body_content_string = '\n'.join(temp_content)

    def get_author(self):
        soup = bs4.BeautifulSoup(requests.get(self.web_url).content, "html.parser")

        # find h1 and then use 'find_all_next' to find any class with 'author'
        title = soup.find("h1")
        regex = re.compile('.*author.*')
        try:
            author_raw = title.find_all_next(attrs={"class": regex})[0].get_text()
        except AttributeError:
            self.author = None
            return

        # delete author title and other info / title() switch to Title case
        author = os.linesep.join([s for s in author_raw.splitlines() if s])
        if author and len(author.split()) > 4:
            self.author = ' '.join(author.split()[:2]).title()
        else:
            self.author = author.title()

    def print_content(self):
        if self.body_content_list is not None:
            for p in self.body_content_list:
                print p
        else:
            print "No content is available"

    def print_article_info(self):
        print "Title:", self.title
        print "By: ", self.author
        print "From:", self.web_url
        print "Pub on:", self.pub_date
        print "Add on:", self.add_date
        number_of_p = len(self.body_content_list)
        print number_of_p, "paragraphs with ", self.word_count, "words"
        if number_of_p > 1:
            print self.body_content_list[0]
            print "....................."
            print self.body_content_list[number_of_p - 1]

    def print_content(self):
        for p in self.body_content_list:
            print p

    def get_sql_query_upload_list(self):
        query_value = [self.title, self.author, self.web_url, self.domain,
                       self.body_content_string, self.pub_date, self.add_date, self.word_count]
        # query_value = ','.join(str(row) for row in query_value)
        return query_value

# url = 'http://cn.nytstyle.com/style/20170221/how-to-live-wisely/?_ga=1.30414655.1698093237.1459196651'
# Crawler(url).print_article_info()
# Crawler(url).print_content()
