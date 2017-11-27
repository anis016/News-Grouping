import common.constants as CONSTANTS
import os
from bson import ObjectId
from common.utils import get_mongo_value
from mongo.MongoDB import MongoDB

from dataprocessing.rake import Rake


def online_processing_rake(document_id, mongo_object):
    document = mongo_object.find_one(CONSTANTS.COLLECTION_SUBSETNEWS,
                                     {"_id": ObjectId(document_id)})
    description = get_mongo_value("cleaned_body", document)
    path = os.getcwd()
    rake = Rake(path)
    candidate_keywords = rake.compute_keywords(description)

    print(candidate_keywords)

def offline_processing_tfidf(document):
    pass

def main(document, mode):
    pass

if __name__ == '__main__':
    main()
