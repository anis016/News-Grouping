from mongo.Mongo import *

mongo = MongoDB()
mongo.initialzie()

print(mongo.get_all_collections())

# mongo.create_collection("testCollection")
# print(mongo.get_all_collections())

# mongo.drop_collection("testCollection")
# print(mongo.get_all_collections())

mongo.describe_collection("newsCollection")
