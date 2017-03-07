from motif_crawler import *


url = 'http://www.latimes.com/business/technology/la-fi-tn-evan-spiegel-snapchat-future-20170302-story.html'
content = Uploadarticle(url).sql_upload()



def redo_crawling():
    url_list = open("url_output.txt", 'r').read().splitlines()
    for url in url_list:
        print url
        article_db = Uploadarticle(str(url))
        article_db.sql_upload()

# re crawl every url in database
# redo_crawling()
