# import sys
# trick to resolve import issue:
# use sys.path to see till what path python sees, then use the path after that.
# print(sys.path)

import time

import common.utils as utils
import common.constants as CONSTANTS

from mongo.MongoDB import MongoDB
from dataprocessing.scraper import ArticleScrape
from dataprocessing.extract_keyword import online_processing_rake

from pymongo import CursorType

retry = 3

def exporting_mongo(document, mongoOb, cnt):

    cnt += 1
    news_scrapperOb = ArticleScrape()
    try:

        # Collect mongo columns - all and then check for url
        mongo_id        = utils.get_mongo_value("_id", document)
        mongo_link      = utils.get_mongo_value("link", document)
        mongo_source    = utils.get_mongo_value("source", document)
        mongo_title     = utils.get_mongo_value("title", document)
        mongo_country   = utils.get_mongo_value("country", document)
        mongo_timestamp = utils.get_mongo_value("timestamp", document)
        mongo_connected = utils.get_mongo_value("connected", document)

        # Check which one has url. generally check if the string starts has "http", "https", "ftp"
        websites = ["http", "ftp", "https", "www"]
        url = ""
        if len([website for website in websites if website in mongo_link]) > 0:
            url = mongo_link
        elif len([website for website in websites if website in mongo_source]) > 0:
            url = mongo_source
        elif len([website for website in websites if website in mongo_title]) > 0:
            url = mongo_title
        elif len([website for website in websites if website in mongo_country]) > 0:
            url = mongo_country
        elif len([website for website in websites if website in mongo_timestamp]) > 0:
            url = mongo_timestamp
        elif len([website for website in websites if website in mongo_connected]) > 0:
            url = mongo_connected

        ## Parsing json
        json = news_scrapperOb.extract_text(url, mongo_timestamp)
        json_error = json.get("error")

        # ignore if any error occurs in parsing newspaper url
        if json_error == "False":

            json_publish_date = json.get("publish_date")
            json_meta_keywords = json.get("meta_keywords")
            json_title = json.get("title")
            json_description = json.get("description")
            json_meta_description = json.get("meta_description")

            cleaned_title = news_scrapperOb.clean_data(json_title)
            cleaned_body = news_scrapperOb.clean_data(json_description)
            cleaned_metabody = news_scrapperOb.clean_data(json_meta_description)

            document_json = {
                "title": mongo_title,
                "link": mongo_link,
                "source": mongo_source,
                "country": mongo_country,
                "timestamp": mongo_timestamp,
                "connected": mongo_connected,
                "scraped_title": json_title,
                "publish_date": str(json_publish_date),  # pymongo date issue occurs, make it string
                "meta_keywords": json_meta_keywords,
                "error": json_error,
                "cleaned_title": cleaned_title,
                "cleaned_body": cleaned_body,
                "cleaned_metabody": cleaned_metabody,
                "url": url,
            }

            processed = utils.mongo_preconditions(**document_json)
            document_json["processed"] = processed

            result = mongoOb.insert(CONSTANTS.COLLECTION_SUBSETNEWS, document_json)
            print("Inserted for value: " + mongo_id)
            # return result.inserted_id

    except Exception as err:
        exception_print = "Mongo ID: {} ".format(mongo_id)
        print(str(err), " ", exception_print )

        # retry 3 times then stop and go for next document
        if cnt <= retry:
            exporting_mongo(document, mongoOb, cnt)


# keep this function always running.
# mongo_listener will always listen to the collection and if any data shows up
# it will send the document to process
def mongo_listener(collection, mongo_object):
    cursor = collection.find({}, cursor_type=CursorType.TAILABLE_AWAIT)
    while True:
        try:
            doc = cursor.next()
            document = collection.find_one({'_id': doc['_id']})
            exporting_mongo(document, mongo_object, 0)
        except StopIteration:
            print("end of cursor, waiting for news document")
            time.sleep(1)
        except Exception as e:
            print("Another exception: " + e)


def main():
    mongoOb = MongoDB()
    db = mongoOb.initialzie()
    collection = db["samplenews"] # get the collection for hearing
    # collection = db["newsCollection"]

    # One time processing
    # Create a new collection of newsCollection to where data needs to be put
    collection_flag = mongoOb.check_collection_exists(CONSTANTS.COLLECTION_SUBSETNEWS)
    if collection_flag is False:
        mongoOb.create_collection(CONSTANTS.COLLECTION_SUBSETNEWS)
        print("Created new Collection: " + CONSTANTS.COLLECTION_SUBSETNEWS)

    # always listen to the collection for data
    mongo_listener(collection, mongoOb)

if __name__ == '__main__':
    main()