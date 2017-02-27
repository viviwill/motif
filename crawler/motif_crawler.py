import MySQLdb
from mercury_parser import *


class Uploadarticle(object):
    # cursor = DbConnection().cursor
    def __init__(self, url):
        self.url = url
        self.article_obj = Crawler(url)
        self.cursor = self.create_db()

    def create_db(self):
        db = MySQLdb.connect(
            host='127.0.0.1',
            user='root',
            passwd='',
            db='motif')

        temp_cursor = db.cursor()
        db.autocommit(True)
        return temp_cursor

    def sql_upload(self):
        cursor = self.cursor
        # try to find the url in the db first
        cursor.execute("SELECT title, add_date FROM motifapp_article "
                       "WHERE web_url = '%s'" % (self.url))
        result = cursor.fetchall()

        if len(result) == 0:
            upload_values = self.article_obj.get_sql_query_upload_list()
            print "Adding new article to db."
            db_fields = "title, author, web_url, domain, body_content, pub_date, add_date, word_count"
            value_place_holder = ','.join('%s' for i in xrange(8))
            upload_query = "INSERT INTO motifapp_article (%s) VALUES (%s)" % (
                db_fields, value_place_holder)
            # print upload_query
            cursor.execute(upload_query, upload_values)
        else:
            # if found any, means the url exist already, then pass
            print "=== Article '%s' is already existed. \n" \
                  "=== It was added on : %s" % (result[0][0], result[0][1])

    def download_url_list(self):
        print "Output urls from db to url_output.txt"
        self.cursor.execute("Select web_url from motifapp_article "
                            "order by date(add_date) ASC")
        result = self.cursor.fetchall()

        output_file = open('url_output.txt', 'w')
        for url in result:
            output_file.write("%s\n" % url[0])

    def print_info(self):
        self.article_obj.print_article_info()

    def get_article_id(self):
        search_id_query = "Select id from motifapp_article WHERE web_url = '%s'" % (self.url)
        print search_id_query
        self.cursor.execute(search_id_query)
        target_article_id = self.cursor.fetchall()[0][0]
        print "Upload article to id: ", target_article_id
        return target_article_id

#
# url_list = open("url_input.txt", 'r').read().splitlines()
# for url in url_list:
#     print url
#     article_db = Uploadarticle(str(url))
#     article_db.print_info()
#     article_db.sql_upload()


url = 'https://hypebeast.com/2017/2/nike-air-max-day-collection'
# Uploadarticle(url).download_url_list()


