import collections
import string

from dataprocessing.similarity_function import DisjointSet, cosine_similarity
from mongo.MongoDB import MongoDB
import common.utils as utils
import common.constants as CONSTANTS
from dataprocessing.tf_idf import TFIDF
from dataprocessing.rake import Rake
import os
from bson import ObjectId

def load_files_and_variables():
    ## Tackle the duplicate entry in mongodb.

    # Read the content of the file and load the idx_list
    ## Below will throw issue when running from different directory in CMD
    # file_path = os.path.join(os.getcwd(), 'data/idx_file.txt')
    # workaround
    dirname, filename = os.path.split(os.path.abspath(__file__))
    # print("dirname: {0}, filename: {1}".format(dirname, filename))
    file_path_mongoId = os.path.join(dirname, 'data/stock_file.txt')
    if os.path.isfile(file_path_mongoId) is False:
        stock_file = open(file_path_mongoId, "w+")  # if file doesn't exist then just create it and then do the write
    else:
        stock_file = open(file_path_mongoId, "r+")
    ## Create a list to check for duplicate entry in mongodb
    stock_list = [line for line in stock_file]
    if len(stock_list) > 0:
        stock_list = stock_list[0].split(",")
        stock_list = stock_list[:len(stock_list) - 1]  # remove the last item which is empty

    return stock_file, stock_list

def stock_matcher(mongo_object, document):
    stock_file, stock_list = load_files_and_variables()
    if str(document['_id']) not in stock_list:

        news_id = str(document["_id"]).strip()
        news_date = document["publish_date"]
        news_meta_keywords = document["meta_keywords"]
        news_description = document["cleaned_body"]

        db = mongo_object.initialzie()
        stock_collection = db[CONSTANTS.COLLECTION_STOCK]
        stock_cursor = stock_collection.find({"Date": news_date},
                                 projection={'_id': True, 'newsLinks': True, 'Date': True,
                                             'description': True},
                                 no_cursor_timeout=True)

        if stock_cursor.count() > 0:

            while True:
                try:
                    stock_document = stock_cursor.next()
                    stock_id = stock_document["_id"]

                    # check if news_link exists, if not then make it
                    # always does this for 1st time
                    news_links = stock_document.get("newsLinks")
                    if news_links is None:
                        mongo_object.update_one(CONSTANTS.COLLECTION_STOCK, {"_id": stock_id}, {'newsLinks': []})

                    stock_description = stock_document["description"]
                    # first filter with stock_date
                    meta_description_list = []
                    # then check if the description matches
                    translator = str.maketrans('', '', string.punctuation)
                    stock_description = stock_description.translate(translator)
                    stock_description = stock_description.lower()

                    if news_meta_keywords is None:
                        meta_description_list.append(False)
                    else:
                        meta_description_list.append(any(stock_description in item for item in news_meta_keywords))
                    if news_description is None:
                        meta_description_list.append(False)
                    else:
                        meta_description_list.append(stock_description in news_description.lower())

                    found = True in meta_description_list
                    if found == True:
                        print("Found, Stock ID: ", stock_id, " News ID: ", news_id)
                        mongo_object.update_list(CONSTANTS.COLLECTION_STOCK, {"_id": stock_id}, {'newsLinks': news_id})

                    stock_list.append(news_id)
                    stock_file.write(news_id + ",")

                except StopIteration:
                    stock_cursor.close()
                    break

                except Exception as e:
                    print("From Stock: ", str(e))
                    stock_cursor.close()
                    break


def update_news_collection(mongo_object, document1, document2):
    document1_objectId = ObjectId(document1)
    document2_objectId = ObjectId(document2)

    mongo_object.update_list(CONSTANTS.COLLECTION_PROCESSED, {"_id": document1_objectId}, {'connected': document1})
    mongo_object.update_list(CONSTANTS.COLLECTION_PROCESSED, {"_id": document2_objectId}, {'connected': document2})

def run_document_similarity(mongo_object, dict_documents):

    tfidf = TFIDF()
    result = tfidf.compute_keywords(dict_documents)
    dsTFIDF = DisjointSet()
    # counter = 0
    for docs_id1, docs_score1 in result.items():
        for docs_id2, docs_score2 in result.items():
            if docs_id1 == docs_id2:
                continue
            docs_score1_value = list(docs_score1[0].values())
            docs_score2_value = list(docs_score2[0].values())

            similarity_score = cosine_similarity(docs_score1_value, docs_score2_value)
            # counter += 1

            if similarity_score >= CONSTANTS.SIMILARITY_THRESHOLD:
                dsTFIDF.add(docs_id1, docs_id2)
                update_news_collection(mongo_object, docs_id1, docs_id2)

    # print("Similarity Score count size: ", counter)
    print("Groups: ", dsTFIDF.group)
    return len(dsTFIDF.group), dsTFIDF.group


def main():
    mongoOb = MongoDB()
    db = mongoOb.initialzie()
    news_collection = db[CONSTANTS.COLLECTION_PROCESSED]
    pageSize = CONSTANTS.BATCH_SIZE
    dict_documents = collections.defaultdict(list)

    # get first ID and process it !
    first_news = news_collection.find_one({},
                                          projection={'_id': True, 'cleaned_body': True, 'country': True,
                                                      'publish_date': True, 'meta_keywords': True}
                                          )
    completed_page_rows = 1
    stock_matcher(mongoOb, first_news)
    object_id = str(first_news.get("_id")).strip()
    cleaned_body = first_news.get("cleaned_body")
    country = first_news.get("country")
    if country == "us":
        dict_documents[object_id].append(cleaned_body)

    last_id = first_news["_id"]

    # get the next page of documents (read-ahead programming style)
    next_results = news_collection.find({"_id": {"$gt": last_id}},
                                        projection={'_id': True, 'cleaned_body': True, 'country': True,
                                                    'publish_date': True, 'meta_keywords': True},
                                        no_cursor_timeout=True).limit(pageSize)

    # keep getting pages until there are no more
    while next_results.count() > 0:

        for ii, document in enumerate(next_results):

            stock_matcher(mongoOb, document)
            object_id = str(document.get("_id")).strip()
            cleaned_body = document.get("cleaned_body")
            country = document.get("country")
            if country == "us":
                dict_documents[object_id].append(cleaned_body)

            completed_page_rows += 1
            if completed_page_rows % pageSize == 0:
                size, group = run_document_similarity(mongoOb, dict_documents)
                print("Processed documents: ", completed_page_rows, ", Matched documents: ", size)

            last_id = document["_id"]

        next_results = news_collection.find({"_id": {"$gt": last_id}},
                                            projection={'_id': True, 'cleaned_body': True, 'country': True,
                                                        'publish_date': True, 'meta_keywords': True},
                                            no_cursor_timeout=True).limit(pageSize)

    print("\nNo More Records. Stopping iterations.\n")

if __name__ == '__main__':
    main()