from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from mongo.MongoDB import MongoDB
import common.constants as CONSTANTS
from bson import ObjectId
from common.utils import get_mongo_value
from pprint import pprint

def index(request):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    news = mongoOb.find("samplenewsSubsetCollection")
    return render(request, "index.html", {'News': news})

def detail(request, id=None):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    news = mongoOb.find("samplenewsSubsetCollection", {"_id": ObjectId(id)})

    for record in news:
        cleaned_title = record['cleaned_title']
        url = record['url']
        connected = record['connected']

    objIds = [x.strip() for x in connected.split(',')]
    documents = []
    for idx, objId in enumerate(objIds):
        documents.append(getSimilarNews(objId))
    #return HttpResponse(news)
    return render(request, "detail.html", {'cleaned_title': cleaned_title, 'url': url, 'similarDocs':documents})

def getSimilarNews(id):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    similarNews = mongoOb.find_one("samplenewsSubsetCollection", {"_id": ObjectId(id)})
    return similarNews

def about(request):
    return render(request, "about.html", {})

def contact(request):
    return render(request, "contact.html", {})
