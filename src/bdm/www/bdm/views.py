from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from mongo.MongoDB import MongoDB
import common.constants as CONSTANTS

def index(request):
    mongoOb = MongoDB()
    mongoOb.initialzie()
    news = mongoOb.find(CONSTANTS.COLLECTION_SUBSETNEWS)
    return render_to_response('index.html', {'News': news}, RequestContext(request))