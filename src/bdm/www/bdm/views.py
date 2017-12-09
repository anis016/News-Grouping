from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from mongo.MongoDB import MongoDB
import common.constants as CONSTANTS
from bson import ObjectId
from common.utils import get_mongo_value
from pprint import pprint
import math

def index(request):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    if request.method == 'POST' and request.POST.get('txtSearch', '') != "" and request.POST.get('page', '') != "":
        total = mongoOb.find("samplenewsSubsetCollection", {"cleaned_title": {"$regex": u".*" + request.POST.get('txtSearch', '').strip() + ".*"}}).count()
        limit = 2
        total_pages = math.ceil(total / limit)
        offset = (int(request.POST.get('page', '')) - 1) * 2;
        nxtPage = int(request.POST.get('page', '')) + 1 if int(request.POST.get('page', '')) < total_pages else ''
        news = mongoOb.find("samplenewsSubsetCollection", {"cleaned_title": {"$regex": u".*" + request.POST.get('txtSearch', '').strip() + ".*"}}).skip(offset).limit(limit)
        if(news.count() != 0):
            return render(request, "index.html", {'news': news, 'txtSearch': request.POST.get('txtSearch', '').strip(), 'nxtPage': nxtPage,  'prevPage': int(request.POST.get('page', '')) - 1})
        else:
            return render(request, "index.html", {})
    else:
        return render(request, "index.html", {})

def stock(request):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    news = mongoOb.find("samplenewsSubsetCollection")
    if(news.count() != 0):
        return render(request, "stock-news.html", {'similarDocs': news})
    else:
        return render(request, "stock-news.html", {})

def detail(request):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    if request.method == 'GET' and request.GET.get('obj', '') != "":
        news = mongoOb.find("samplenewsSubsetCollection", {"_id": ObjectId(request.GET.get('obj', '').strip())})
        for record in news:
            cleaned_title = record['cleaned_title']
            url = record['url']
            connected = record['connected']

        if(connected != "None"):
            objIds = [x.strip() for x in connected.split(',')]
            documents = []
            for docId in objIds:
                documents.append(getSimilarNews(docId))
            #return HttpResponse(documents)
            return render(request, "detail.html", {'cleaned_title': cleaned_title, 'url': url, 'news_stats':3, 'similarDocs': documents})
        else:
            return render(request, "detail.html", {'cleaned_title': cleaned_title, 'url': url})

def getSimilarNews(docId):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    similarNews = mongoOb.find_one("samplenewsSubsetCollection", {"_id": ObjectId(docId)})
    return similarNews

def about(request):
    return render(request, "about.html", {})

def contact(request):
    return render(request, "contact.html", {})
