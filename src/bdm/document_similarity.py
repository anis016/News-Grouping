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

def add_documents(mongo_object, batch_count):
    dict_documents = collections.defaultdict(list)
    current_algorithm = CONSTANTS.SIMILARITY_ALGORITHM
    try:
        counter = 0;
        cursor = mongo_object.find(CONSTANTS.COLLECTION_PROCESSED)
        for document in cursor:
            stock_matcher(mongo_object, document)

            object_id = str(document.get("_id")).strip()
            cleaned_body = document.get("cleaned_body")
            country = document.get("country")

            keyword_algorithm = utils.get_mongo_value(current_algorithm, document)
            if keyword_algorithm != current_algorithm:
                if country == "us":
                    dict_documents[object_id].append(cleaned_body)
                    counter += 1

            if counter == batch_count:
                break

    except Exception as err:
        print(str(err))

    return dict_documents

def stock_matcher(mongo_object, document):
    stock_file, stock_list = load_files_and_variables()
    if str(document['_id']) not in stock_list:
        news_id = str(document["_id"]).strip()
        news_date = document["publish_date"]
        news_meta_keywords = document["meta_keywords"]
        news_description = document["cleaned_body"]

        stock_cursor = mongo_object.find(CONSTANTS.COLLECTION_STOCK)
        for stock_document in stock_cursor:
            found = False
            stock_id = stock_document["_id"]

            # check if news_link exists, if not then make it
            # always does this for 1st time
            news_links = stock_document.get("newsLinks")
            if news_links is None:
                mongo_object.update_one(CONSTANTS.COLLECTION_STOCK, {"_id": stock_id}, {'newsLinks': []})

            stock_date = stock_document["Date"]
            stock_description = stock_document["description"]
            # first filter with stock_date
            meta_description_list = []
            if stock_date == news_date:
                # then check if the description matches
                translator = str.maketrans('', '', string.punctuation)
                stock_description = stock_description.translate(translator)
                stock_description = stock_description.lower()

                meta_description_list.append(any(stock_description in item for item in news_meta_keywords))
                meta_description_list.append(stock_description in news_description.lower())

                found = True in meta_description_list
                if found == True:
                    mongo_object.update_list(CONSTANTS.COLLECTION_STOCK, {"_id": stock_id}, {'newsLinks': news_id})
            else:
                continue

        stock_list.append(news_id)
        stock_file.write(news_id + ",")

def update_news_collection(mongo_object, document1, document2):
    document1_objectId = ObjectId(document1)
    document2_objectId = ObjectId(document1)

    mongo_object.update_list(CONSTANTS.COLLECTION_PROCESSED, {"_id": document1_objectId}, {'connected': document1})
    mongo_object.update_list(CONSTANTS.COLLECTION_PROCESSED, {"_id": document2_objectId}, {'connected': document2})

def run_document_similarity(mongo_object, dict_documents):

    tfidf = TFIDF()
    result = tfidf.compute_keywords(dict_documents)
    dsTFIDF = DisjointSet()

    for docs_id1, docs_score1 in result.items():
        for docs_id2, docs_score2 in result.items():
            if docs_id1 == docs_id2:
                continue
            docs_score1_value = list(docs_score1[0].values())
            docs_score2_value = list(docs_score2[0].values())

            similarity_score = cosine_similarity(docs_score1_value, docs_score2_value)

            if similarity_score >= CONSTANTS.SIMILARITY_THRESHOLD:
                dsTFIDF.add(docs_id1, docs_id2)
                update_news_collection(mongo_object, docs_id1, docs_id2)

    return len(dsTFIDF.group), dsTFIDF.group


def main():
    mongoOb = MongoDB()
    db = mongoOb.initialzie()
    # collection = db[CONSTANTS.COLLECTION_PROCESSED]

    counter = 1
    while True:
        stats = db.command('collStats', CONSTANTS.COLLECTION_PROCESSED)
        count = stats['count']
        # print(stats)

        # if count > 0 and count%CONSTANTS.BATCH_SIZE == 0:
        batch_count = counter * CONSTANTS.BATCH_SIZE

        print("counter value: ", batch_count)
        dict_documents = add_documents(mongoOb, batch_count)
        size, group = run_document_similarity(mongoOb, dict_documents)

        print(batch_count, " matched documents: ", size)

        if batch_count >= count:
            break

        counter += 1
if __name__ == '__main__':
    main()