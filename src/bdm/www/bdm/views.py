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
        total = mongoOb.find("samplenewsSubsetCollection", {"$or": [{"cleaned_title": {"$regex": u".*" + txtSearch + ".*"}}, {"cleaned_body": {"$regex": u".*" + txtSearch + ".*"}}]}
).count()
        limit = 2
        total_pages = math.ceil(total / limit)
        offset = (int(request.POST.get('page', '')) - 1) * 2;
        nxtPage = int(request.POST.get('page', '')) + 1 if int(request.POST.get('page', '')) < total_pages else ''
        news = mongoOb.find("samplenewsSubsetCollection", {"$or": [{"cleaned_title": {"$regex": u".*" + txtSearch + ".*"}}, {"cleaned_body": {"$regex": u".*" + txtSearch + ".*"}}]}
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
        totalNews = mongoOb.find("samplenewsSubsetCollection").count()
        news = mongoOb.find("samplenewsSubsetCollection", {"_id": ObjectId(request.GET.get('obj', '').strip())})
        for record in news:
            cleaned_title = record['cleaned_title']
            url = record['url']
            connected = record['connected']

        connected.remove("None") if connected[0]=="None" else ''
        unlikeNews = totalNews - len(connected)
        unlikeNewsProp = float(unlikeNews) * (100.0 / totalNews)
        similarNewsProp = float(len(connected)) * (100.0 / totalNews)
        documents = []
        for docId in connected:
            if(docId != ""):
                documents.append(getSimilarNews(docId))
        return render(request, "detail.html", {'cleaned_title': cleaned_title, 'url': url, 'similarNews': similarNewsProp, 'unlikeNews': unlikeNewsProp, 'similarDocs': documents})
    else:
        return render(request, "detail.html", {})

def getSimilarNews(docId):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    similarNews = mongoOb.find_one("samplenewsSubsetCollection", {"_id": ObjectId(docId)})
    return similarNews

def about(request):
    return render(request, "about.html", {})

def contact(request):
    return render(request, "contact.html", {})
