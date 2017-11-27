from pymongo import errors
from pymongo import MongoClient

import common.constants as CONSTANTS

class MongoDB:

    URI = CONSTANTS.MONGO_URI
    DATABASE = None

    @staticmethod
    def initialzie():
        client = MongoClient(MongoDB.URI)
        MongoDB.DATABASE = client[CONSTANTS.DATABASE_NAME]

        return MongoDB.DATABASE

    @staticmethod
    def insert(collection, data):
        result = MongoDB.DATABASE[collection].insert_one(data)
        return result

    @staticmethod
    def find_one(collection, query=None):
        if query != None:
            return MongoDB.DATABASE[collection].find_one(query)
        else:
            return MongoDB.DATABASE[collection].find_one()

    @staticmethod
    def find(collection, query=None):
        if query != None:
            return MongoDB.DATABASE[collection].find(query)
        else:
            return MongoDB.DATABASE[collection].find()

    @staticmethod
    def update(collection, query, data):
        return MongoDB.DATABASE[collection].update(query, data, upsert=True)

    @staticmethod
    def delete(collection, query):
        return MongoDB.DATABASE[collection].remove(query)

    @staticmethod
    def get_all_collections():
        return MongoDB.DATABASE.collection_names(include_system_collections=False);

    @staticmethod
    def check_collection_exists(collection):
        collections = MongoDB.get_all_collections()
        if collection in collections:
            return True
        return False

    @staticmethod
    def create_collection(name):
        try:
            MongoDB.DATABASE.create_collection(name);
        # http://api.mongodb.com/python/current/api/pymongo/errors.html
        except errors.CollectionInvalid as e:
            print(e)
        else:
            return True # returns True, if collection creation is success

    @staticmethod
    def drop_collection(name):
        collections = MongoDB.get_all_collections()
        if name in collections:
            collection = MongoDB.DATABASE[name]
            collection.drop()
            print("Collection: '{0}' droppped".format(name))
        else:
            print("Collection: '{0}' donot exists".format(name))

    # This will take time depending upon the collection size
    @staticmethod
    def describe_collection(name):

        collection = MongoDB.find(name)
        keylist = []
        for item in collection:
            for key in item.keys():
                if key not in keylist:
                    keylist.append(key)

        keylist.sort()
        print(name + " Metadata")
        for key in keylist:
            print("%s" % (key))