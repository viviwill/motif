import MySQLdb
from mercury_parser import *


class Uploadarticle(object):
    # cursor = DbConnection().cursor
    def __init__(self, url):
        self.url = url
        self.db_field_list = ["title", "author", "web_url", "lead_image_url", "domain",
                              "body_content", "pub_date", "add_date", "word_count"]
        self.article_obj = Crawler(url)
        self.sql_query_value = self.article_obj.get_sql_query_list()
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

        # merge db_field_list into one
        db_field = ','.join(i for i in self.db_field_list)

        if len(result) == 0:
            print "Adding new article to db."
            value_place_holder = ','.join('%s' for i in xrange(len(self.db_field_list)))
            upload_query = "INSERT INTO motifapp_article (%s) VALUES (%s)" % (
                db_field, value_place_holder)
            print upload_query
            cursor.execute(upload_query, self.sql_query_value)

        # if found any, means the url exist already, then pass
        else:
            print "=== Article '%s' was added on : %s" % (result[0][0], result[0][1])
            print "Updating content ... "
            set_query = "UPDATE motifapp_article SET " + ' = %s,'.join(
                i for i in self.db_field_list) + '= %s '
            where_query = "WHERE web_url = %s"
            update_query = set_query + where_query

            # update db
            query_value = self.sql_query_value
            query_value.append(self.url)
            cursor.execute(update_query, query_value)

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


