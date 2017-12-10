from mongo.MongoDB import MongoDB

st = "2016-06-22"

# Date.UTC(1970, 9, 21)]

import datetime
import time

# timestamp = time.mktime(datetime.datetime.strptime(st, "%Y-%m-%d").timetuple())
# print(timestamp)

mongo_ob = MongoDB()
db = mongo_ob.initialzie()
collection = db["samplestock"]
stock_cursor = collection.find()

for stock in stock_cursor:
    item = [stock["Date"], float(stock["Adj_Close"])]
    print(item)