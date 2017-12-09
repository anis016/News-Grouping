import collections

from mongo.MongoDB import MongoDB
import common.utils as utils
import common.constants as CONSTANTS
from dataprocessing.tf_idf import TFIDF
from dataprocessing.rake import Rake
import os

def add_documents(mongo_object):
    dict_documents = collections.defaultdict(list)
    current_algorithm = CONSTANTS.SIMILARITY_ALGORITHM
    try:
        cursor = mongo_object.find(CONSTANTS.COLLECTION_PROCESSED)
        for document in cursor:
            object_id = str(document.get("_id")).strip()
            cleaned_body = document.get("cleaned_body")
            country = document.get("country")

            keyword_algorithm = utils.get_mongo_value(current_algorithm, document)
            if keyword_algorithm != current_algorithm:
                if country == "us":
                    dict_documents[object_id].append(cleaned_body)

    except Exception as err:
        print(str(err))

    return dict_documents

def run_document_similarity(dict_documents):
    pass

def main():
    mongoOb = MongoDB()
    db = mongoOb.initialzie()
    # collection = db[CONSTANTS.COLLECTION_PROCESSED]

    stats = db.command('collStats', CONSTANTS.COLLECTION_PROCESSED)
    print(stats)

    dict_documents = add_documents(mongoOb)

    run_document_similarity(dict_documents)


if __name__ == '__main__':
    main()