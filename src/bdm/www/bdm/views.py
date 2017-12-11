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
        limit = 1
        total_pages = math.ceil(total / limit)
        offset = (int(request.POST.get('page', '')) - 1) * limit;
        nxtPage = int(request.POST.get('page', '')) + 1 if int(request.POST.get('page', '')) < total_pages else ''
        news = mongoOb.find(CONSTANTS.COLLECTION_PROCESSED, {"$or": [{"cleaned_title": {"$regex": u".*" + txtSearch + ".*"}}, {"cleaned_body": {"$regex": u".*" + txtSearch + ".*"}}]}
).skip(offset).limit(limit)
        if(news.count() != 0):
            return render(request, "index.html", {'news': news, 'txtSearch': txtSearch, 'nxtPage': nxtPage,  'prevPage': int(request.POST.get('page', '')) - 1})
        else:
            return render(request, "index.html", {})
    else:
        return render(request, "index.html", {})

def stock(request):
    mongoOb = MongoDB()
    mongoOb.initialzie()
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
        connected_news_list = collections.defaultdict(list)
        for stock in stocks:
            stockDateVal.append(time.mktime(datetime.strptime(stock.get('Date'), "%Y-%m-%d").timetuple()))
            stockCloseVal.append(float (stock.get('Adj_Close')))

            news_link_lists = stock["newsLinks"]
            for item in news_link_lists:
                if item not in connected_news_list[stock["Date"]]:
                    connected_news_list[stock["Date"]].append(item)

        if len(connected_news_list) > 0:
            connected_news_list["size"] = len(connected_news_list)

        stockDate = ','.join(map(str, stockDateVal))
        stockClose = ','.join(map(str, stockCloseVal))

        if(stocks.count() != 0):
            data = {'stockDateVal': stockDate,
                    'stockCloseVal': stockClose,
                    'ticker': ticker,
                    'startDate': startDate,
                    'endDate': endDate,
                    'grouped_news': connected_news_list,
                    'stockChart': True}

            return render(request, "stock-news.html", data)
        else:
            return render(request, "stock-news.html", {})
    else:
        return render(request, "stock-news.html", {})

def detail(request):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    if request.method == 'GET' and request.GET.get('obj', '') != "":
        obj = request.GET.get('obj', '').strip()
        page = int(request.GET.get('page', '').strip()) if request.GET.get('page', '') else 1
        totalNews = mongoOb.find(CONSTANTS.COLLECTION_PROCESSED).count()
        news = mongoOb.find(CONSTANTS.COLLECTION_PROCESSED, {"_id": ObjectId(obj)})
        for record in news:
            cleaned_title = record['cleaned_title']
            url = record['url']
            connected = record['connected']

        connected.remove("None") if connected[0]=="None" else ''
        total = len(connected)
        unlikeNews = totalNews - total
        unlikeNewsProp = float(unlikeNews) * (100.0 / totalNews)
        similarNewsProp = float(total) * (100.0 / totalNews)

        if request.GET.get('next', '') and request.GET.get('until', ''):
            until = int(request.GET.get('until', '')) + 1
        elif (request.GET.get('prev', '') and request.GET.get('until', '')):
            until = int(request.GET.get('until', '')) - 1
        else:
            until = 1

        limit = 1
        total_pages = math.ceil(total / limit)
        offset = (int(page) - 1) * limit;
        nxtPage = int(page) + 1 if int(page) < total_pages else ''
        #return HttpResponse(offset)

        documents = []
        for x in range(offset, until):
            if (connected[x] != ""):
                print(connected[x])
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
