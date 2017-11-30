from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from mongo.MongoDB import MongoDB
import common.constants as CONSTANTS

def index(request):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    news = mongoOb.find(CONSTANTS.COLLECTION_SUBSETNEWS)
    return render(request, "index.html", {'News': news})

def detail(request, id=None):
    return HttpResponse("hahaha")

def about(request):
    return render(request, "about.html", {})

def contact(request):
    return render(request, "contact.html", {})
