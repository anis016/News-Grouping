import collections

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from mongo.MongoDB import MongoDB
import common.constants as CONSTANTS
from bson import ObjectId
from common.utils import get_mongo_value
from pprint import pprint
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone
import time
import math

def index(request):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    if request.method == 'POST' and request.POST.get('txtSearch', '') != "" and request.POST.get('page', '') != "":
        txtSearch = request.POST.get('txtSearch', '').strip()
        total = mongoOb.find(CONSTANTS.COLLECTION_PROCESSED, {"$or": [{"cleaned_title": {"$regex": u".*" + txtSearch + ".*"}}, {"cleaned_body": {"$regex": u".*" + txtSearch + ".*"}}]}
).count()
        limit = 12
        total_pages = math.ceil(total / limit)
        offset = (int(request.POST.get('page', '')) - 1) * limit;
        nxtPage = int(request.POST.get('page', '')) + 1 if int(request.POST.get('page', '')) < total_pages else ''
        news = mongoOb.find(CONSTANTS.COLLECTION_PROCESSED, {"$or": [{"cleaned_title": {"$regex": u".*" + txtSearch + ".*"}}, {"cleaned_body": {"$regex": u".*" + txtSearch + ".*"}}]}
).skip(offset).limit(limit)
        if(news.count() != 0):
            return render(request, "index.html", {'news': news,
                                                  'txtSearch': txtSearch,
                                                  'nxtPage': nxtPage,
                                                  'prevPage': int(request.POST.get('page', '')) - 1})
        else:
            return render(request, "index.html", {})
    else:
        return render(request, "index.html", {})

def stock(request):
    mongoOb = MongoDB()
    db = mongoOb.initialzie()

    if request.method == 'POST' and request.POST.get('ticker', '') != ""  and request.POST.get('startDate', '') != "" and request.POST.get('endDate', '') != "":
        ticker = request.POST.get('ticker', '').strip()
        startDate = request.POST.get('startDate', '').strip()
        endDate = request.POST.get('endDate', '').strip()

        stocks = mongoOb.find(CONSTANTS.COLLECTION_STOCK,
                              {"$and": [
                                  {"Ticker": ticker},
                                  {"Date": {"$gte": startDate, "$lte": endDate}}
                              ]})

        stockCloseVal = []
        stockDateVal = []
        news_group_date = []
        for stock in stocks:
            stockDateVal.append(time.mktime(datetime.strptime(stock.get('Date'), "%Y-%m-%d").timetuple()))
            stockCloseVal.append(float (stock.get('Adj_Close')))

            newsLinks = stock["newsLinks"]
            if len(newsLinks) > 0:
                news_object_list = []
                for news in newsLinks:
                    news_collection = db[CONSTANTS.COLLECTION_PROCESSED]
                    news_object = news_collection.find_one({"_id": ObjectId(news)},
                                                          projection={'_id': True,
                                                                      'cleaned_title': True}
                                                          )
                    news_object_list.append(news_object)


                news_group_date.append([ stock["Date"], news_object_list])

        stockDate = ','.join(map(str, stockDateVal))
        stockClose = ','.join(map(str, stockCloseVal))

        if(stocks.count() != 0):
            data = {'stockDateVal': stockDate,
                    'stockCloseVal': stockClose,
                    'ticker': ticker,
                    'startDate': startDate,
                    'endDate': endDate,
                    'grouped_news': news_group_date,
                    'stockChart': True}

            return render(request, "stock-news.html", data)
        else:
            return render(request, "stock-news.html", {})
    else:
        return render(request, "stock-news.html", {})

def detail(request):
    mongoOb = MongoDB()
    db = mongoOb.initialzie()
    stats = db.command("collstats", CONSTANTS.COLLECTION_PROCESSED)
    count = stats["count"]
    if request.method == 'GET' and request.GET.get('obj', '') != "":
        obj = request.GET.get('obj', '').strip()
        page = int(request.GET.get('page', '').strip()) if request.GET.get('page', '') else 1
        # totalNews = mongoOb.find(CONSTANTS.COLLECTION_PROCESSED).count()
        totalNews = count

        # news = mongoOb.find(CONSTANTS.COLLECTION_PROCESSED, {"_id": ObjectId(obj)})
        news_collection = db[CONSTANTS.COLLECTION_PROCESSED]
        news = news_collection.find_one({"_id": ObjectId(obj)},
                             projection={'_id': True, 'cleaned_title': True, 'url': True,
                                         'connected': True},
                             no_cursor_timeout=True)

        cleaned_title = news['cleaned_title']
        url = news['url']
        connected = news['connected']

        # try:
        #     if connected[0] == "None":
        #         connected.remove("None")
        # except Exception as e:
        #     print(str(e))


        # for pie chart
        total = len(connected)
        unlikeNews = totalNews - total
        unlikeNewsProp = float(unlikeNews) * (100.0 / totalNews)
        similarNewsProp = float(total) * (100.0 / totalNews)
        # for pie chart

        # for pagination
        if request.GET.get('next', '') and request.GET.get('until', ''):
            until = int(request.GET.get('until', '')) + 5
        elif (request.GET.get('prev', '') and request.GET.get('until', '')):
            until = int(request.GET.get('until', '')) - 5
        else:
            until = 5

        limit = 5
        total_pages = math.ceil(total / limit)
        offset = (int(page) - 1) * limit;
        nxtPage = int(page) + 1 if int(page) < total_pages else ""
        #return HttpResponse(offset)


        # Condition: 1
        until = len(connected) if len(connected) < until else until

        documents = []
        # for it, item in enumerate(connected):
        #     documents.append(getSimilarNews(item))

        if len(connected) > 0:
            for x in range(offset, until):
                #if (connected[x]):
                    # print(connected[x])
                documents.append(getSimilarNews(connected[x]))
        #for docId in connected:
            #if(docId != ""):
                #documents.append(getSimilarNews(docId))

        return render(request, "detail.html", {'cleaned_title': cleaned_title,
                                               'url': url,
                                               'similarNews': similarNewsProp,
                                               'unlikeNews': unlikeNewsProp,
                                               'similarDocs': documents,
                                               'obj': obj,
                                               'until': until,
                                               'nxtPage': nxtPage,
                                               'prevPage': int(page) - 1})
    else:
        return render(request, "detail.html", {})

def getSimilarNews(docId):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    similarNews = mongoOb.find_one(CONSTANTS.COLLECTION_PROCESSED, {"_id": ObjectId(docId)})
    return similarNews

def about(request):
    return render(request, "about.html", {})

def contact(request):
    return render(request, "contact.html", {})
