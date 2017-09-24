from mongo.MongoDB import *
from dataprocessing.scraper import *
import common.constants as CONSTANTS
import os
import sys
from common.utils import *

if __name__ == '__main__':

    mongoOb = MongoDB()
    news_scrapperOb = ArticleScrape()

    mongoOb.initialzie()

    # Create a new subset collection of newsCollection
    mongoOb.create_collection(CONSTANTS.COLLECTION_SUBSETNEWS)

    # Track the file writting in mongo
    file_path_traces = os.path.join(os.getcwd(), 'data/processed_file.txt')
    traces_file = open(file_path_traces, "r+")

    # print(mongoOb.get_all_collections())
    # print(mongoOb.describe_collection("newsCollection"))

    ## Tackle the duplicate entry in mongodb
    # First read the content of the file and load the idx_list

    file_path = os.path.join(os.getcwd(), 'data/idx_file.txt')
    if os.path.isfile(file_path) is False:
        idx_file = open(file_path, "w+")  # if file doesn't exist then just create it and then do the write
    else:
        idx_file = open(file_path, "r+")

    # Create a list to check for duplicate entry in mongodb
    idx_list = []
    idx_list = [line for line in idx_file]

    if len(idx_list) > 0:
        idx_list = idx_list[0].split(",")
        idx_list = idx_list[:len(idx_list)-1] # remove the last item which is empty

    try:

        news_cursor = mongoOb.find(CONSTANTS.COLLECTION_NEWS)
        # news_cursor = mongoOb.find(CONSTANTS.COLLECTION_NEWS, {'id': '"818"'}) # for debugging purpose
        for document in news_cursor:
            mongo_id = str(document.get("id")).strip()

            if mongo_id != "None":
                mongo_id = str(document.get("id")).strip().split('"')[1]

                if mongo_id not in idx_list:
                    idx_list.append(mongo_id)

                    # mongoOb.delete(CONSTANTS.COLLECTION_TEST, {"id": mongo_id})

                    # Collect mongo columns - all and then check for url
                    mongo_link = get_mongo_value("link", document)
                    mongo_source = get_mongo_value("source", document)
                    mongo_title = get_mongo_value("title", document)
                    mongo_country = get_mongo_value("country", document)
                    mongo_timestamp = get_mongo_value("timestamp", document)
                    mongo_connected = get_mongo_value("connected", document)

                    # if is_website(mongo_link):
                    #     url = mongo_link
                    # elif is_website(mongo_source):
                    #     url = mongo_source
                    # elif is_website(mongo_country):
                    #     url = mongo_country
                    # elif is_website(mongo_timestamp):
                    #     url = mongo_timestamp
                    # elif is_website(mongo_connected):
                    #     url = mongo_connected
                    # elif is_website(mongo_title):
                    #     url = mongo_title

                    ## Naive approach
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

                    if url != "None":
                        mongo__id = document.get("_id")

                        ## Parsing json
                        json = news_scrapperOb.extract_text(url, mongo_timestamp, mongo_id)
                        json_publish_date     = json.get("publish_date")
                        json_metakeywords     = json.get("meta_keywords")
                        json_error            = json.get("error")
                        json_title            = json.get("title")
                        json_description      = json.get("description")
                        json_meta_description = json.get("meta_description")

                        if json_error == "False":
                            cleaned_title = news_scrapperOb.clean_data(json_title)
                            cleaned_body = news_scrapperOb.clean_data(json_description)
                            cleaned_metabody = news_scrapperOb.clean_data(json_meta_description)
                        else:
                            cleaned_title = None
                            cleaned_body = None
                            cleaned_metabody = None

                        # if everything is alright then make it processed=True
                        document_json = {
                                         "id"              : mongo_id,
                                         "title"           : mongo_title,
                                         "link"            : mongo_link,
                                         "source"          : mongo_source,
                                         "country"         : mongo_country,
                                         "timestamp"       : mongo_timestamp,
                                         "connected"       : mongo_connected,
                                         "scraped_title"   : json_title,
                                         "publish_date"    : str(json_publish_date), # pymongo date issue occurs, just make it string
                                         "meta_keywords"   : json_metakeywords,
                                         "error"           : json_error,
                                         "cleaned_title"   : cleaned_title,
                                         "cleaned_body"    : cleaned_body,
                                         "cleaned_metabody": cleaned_metabody,
                                         "url"             : url,
                                        }

                        if json_error == "False":
                            processed = mongo_preconditions(**document_json)
                            document_json["processed"] = processed
                        else:
                            document_json["processed"] = json_error

                        # mongoOb.update(CONSTANTS.COLLECTION_SUBSETTEST, {"_id": mongo__id}, document_json)
                        mongoOb.insert(CONSTANTS.COLLECTION_SUBSETNEWS, document_json)
                        idx_file.write(mongo_id + ",") # append only if insertion is success

                        file_print = "Processed ID: {}, Title: {} ---- Error - '{}'\n".format(mongo_id, json_title, json_error)
                        print(file_print)
                        traces_file.write(file_print)
    except Exception as err:
        exception_print = "Some Error occured. Last Mongo ID: {} ".format(mongo_id)
        print(exception_print)
        print(str(err))
        sys.exit(1)

    idx_file.close()
    traces_file.close()