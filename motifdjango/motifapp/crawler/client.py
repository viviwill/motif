from motif_crawler import *


url = 'http://www.newyorker.com/magazine/2017/04/10/march-madness-in-the-meatpacking-district'
content = Uploadarticle(url).print_info()


# you&apos;re

def redo_crawling():
    url_list = open("url_output.txt", 'r').read().splitlines()
    for url in url_list:
        print url
        article_db = Uploadarticle(str(url))
        article_db.sql_upload()

# re crawl every url in database
# redo_crawling()
