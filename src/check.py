import pymongo

client = pymongo.MongoClient()
db = client['businessData']
news_collection = db["samplenewsSubsetCollection"]

print("Collection contains %s documents." % db.command("collstats", "samplenewsSubsetCollection")["count"])

# get first ID
pageSize = 5
first_news = news_collection.find_one()
completed_page_rows=1
last_id = first_news["_id"]

# get the next page of documents (read-ahead programming style)
next_results = news_collection.find({"_id":{"$gt":last_id}},{"link":1},no_cursor_timeout=True).limit(pageSize)

# keep getting pages until there are no more
while next_results.count()>0:
  for ii, document in enumerate(next_results):
    completed_page_rows+=1
    if completed_page_rows % pageSize == 0:
      print("%s (id = %s): link %s" % (completed_page_rows,document["_id"],document["link"]))
    last_id = document["_id"]

  next_results = news_collection.find({"_id":{"$gt":last_id}},{"link":1},no_cursor_timeout=True).limit(pageSize)

print("\nDone.\n")