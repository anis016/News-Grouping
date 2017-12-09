# trick to resolve import issue:
# use sys.path to see till what path python sees, then use the path after that.
# import sys
# print(sys.path)
import json
import time

import common.utils as utils
import common.constants as CONSTANTS
import os

from mongo.MongoDB import MongoDB
from dataprocessing.scraper import ArticleScrape

from pymongo import CursorType

retry = 3

def exporting_mongo(document, mongoOb, cnt):

    cnt += 1
    news_scrapperOb = ArticleScrape()
    try:

        # Collect mongo columns - all and then check for url
        mongo_id        = utils.get_mongo_value("_id", document)
        mongo_record_id = utils.get_mongo_value("id", document)
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
                "id": mongo_record_id,
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

            result = mongoOb.insert(CONSTANTS.COLLECTION_PROCESSED, document_json)
            print("Inserted for value: " + mongo_id)
            return result.inserted_id

    except Exception as err:
        exception_print = "Mongo ID: {} ".format(mongo_id)
        print(str(err), " ", exception_print )

        # retry 3 times then stop and go for next document
        if cnt <= retry:
            exporting_mongo(document, mongoOb, cnt)

def load_files_and_variables():
    ## Tackle the duplicate entry in mongodb.

    # Read the content of the file and load the idx_list
    ## Below will throw issue when running from different directory in CMD
    # file_path = os.path.join(os.getcwd(), 'data/idx_file.txt')
    # workaround
    dirname, filename = os.path.split(os.path.abspath(__file__))
    # print("dirname: {0}, filename: {1}".format(dirname, filename))
    file_path_mongoId = os.path.join(dirname, 'data/idx_file.txt')
    if os.path.isfile(file_path_mongoId) is False:
        idx_file = open(file_path_mongoId, "w+")  # if file doesn't exist then just create it and then do the write
    else:
        idx_file = open(file_path_mongoId, "r+")
    ## Create a list to check for duplicate entry in mongodb
    idx_list = [line for line in idx_file]
    if len(idx_list) > 0:
        idx_list = idx_list[0].split(",")
        idx_list = idx_list[:len(idx_list) - 1]  # remove the last item which is empty

    return idx_file, idx_list

# keep this function always running.
# mongo_listener will always listen to the collection and if any data shows up
# it will send the document to process
def mongo_listener(collection, mongo_object):

    idx_file, idx_list = load_files_and_variables()

    cursor = collection.find({}, cursor_type=CursorType.TAILABLE_AWAIT, no_cursor_timeout=True).batch_size(5)
    while True:
        try:
            document = cursor.next()

            # first check if there is a connected field value
            connected_id = document.get("connected")
            connected_objectId = "None"
            if connected_id != "NULL":
                next_connected_object = mongo_object.find_one(CONSTANTS.COLLECTION_PROCESSED, {'id': connected_id})
                if next_connected_object is not None:
                    connected_objectId = next_connected_object["_id"]
                else:
                    connected_document = collection.find_one({'id': connected_id})
                    connected_objectId = exporting_mongo(connected_document, mongo_object, 0)
                    if str(connected_document['_id']) not in idx_list:
                        idx_list.append(str(connected_document['_id']))
                        idx_file.write(str(connected_document['_id']) + ",")

            document["connected"] = connected_objectId
            # document = collection.find_one({'_id': doc['_id']})
            if str(document['_id']) not in idx_list:
                exporting_mongo(document, mongo_object, 0)
                idx_list.append(str(document['_id']))
                idx_file.write(str(document['_id'])+ ",")
            else:
                print(str(document['_id']) + " already processed!")

        except StopIteration as se:
            print("end of cursor, waiting for news document ")
            time.sleep(1)
        except Exception as e:
            cursor.close()
            idx_file.close()
            print("Another exception: " + e)


def main():
    mongoOb = MongoDB()
    db = mongoOb.initialzie()
    # collection = db["samplenews"] # testing
    collection = db[CONSTANTS.COLLECTION_LISTENER]

    # One time processing
    # Create a new processing collection for the listener collection.
    # the data needs to be put here after fetching and cleaning.
    collection_flag = mongoOb.check_collection_exists(CONSTANTS.COLLECTION_PROCESSED)
    if collection_flag is False:
        mongoOb.create_collection(CONSTANTS.COLLECTION_PROCESSED, "_id")
        print("Created new Collection: " + CONSTANTS.COLLECTION_PROCESSED)

    # always listen to the collection for data
    mongo_listener(collection, mongoOb)

if __name__ == '__main__':
    main()
