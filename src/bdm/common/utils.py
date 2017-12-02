import datetime
import json
import socket

import os
from dateutil.parser import parse
import re
import datefinder

def convertTimeStampToDataTime(timeStamp):
    return datetime.datetime.fromtimestamp(int(timeStamp)).strftime("%Y-%m-%d")


def parse_date(article):
    meta_data = article.meta_data
    # parse dict
    publish_date = None
    for elem_key, elem_value in meta_data.items():
        if "date" in elem_key:
            if is_date(elem_value):
                publish_date = date_finder(elem_value)
                if publish_date is not None:
                    return publish_date.date()
        elif isinstance(elem_value, dict):
            for inner_elem_key, inner_elem_value in elem_value.items():
                if "date" in inner_elem_key:
                    if is_date(inner_elem_value):
                        publish_date = date_finder(elem_value)
                        if publish_date is not None:
                            return publish_date.date()

    if publish_date is None:
        publish_date = date_finder(article.meta_description)
        if publish_date is not None:
            return publish_date.date()

def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False

def is_date(st):
    try:
        parse(st) # dateutil parser.parse
        return True
    except ValueError:
        return False

def is_date_timestamp(timeStamp):
    try:
        datetime.datetime.fromtimestamp(int(timeStamp)).strftime("%Y-%m-%d")
        return True
    except :
        # just return False
        return False

def get_date(st):
    parse_date = re.compile(r"([\d]{4}-[\d]{2}-[\d]{2})", re.UNICODE).split(st)
    return datetime.datetime.strptime(parse_date[1], "%Y-%m-%d").date()

def date_finder(st):
    matches = datefinder.find_dates(st)
    for match in matches:
        return match
    else:
        return None

def is_website(url):
    try:
        import requests
        requests.get(url)
        return True
    except:
        return False

def parse_keywords(article):
    meta_data = article.meta_data
    # parse dict
    keywords_list = []
    for elem_key, elem_value in meta_data.items():
        if "keyword" in elem_key:
            keywords_list = [elem for elem in elem_value.split(',')]
            return keywords_list
        elif isinstance(elem_value, dict):
            for inner_elem_key, inner_elem_value in elem_value.items():
                if "keyword" in inner_elem_key:
                    keywords_list = [elem for elem in elem_value.split(',')]
                    return keywords_list


def mongo_preconditions(**kwargs):

    check = True
    for elem in kwargs.items():
        key, value = elem[0], elem[1]
        if "clean" in key:
            # check if "meta-body":
            if "meta" in key and (value is None or len(value) <= 0):
                check = "Cleaned Meta-Body is Empty"
            elif "_body" in key and (value is None or len(value) <= 0):
                check = "Cleaned Body is Empty"
            if "title" in key and (value is None or len(value) <= 0):
                check = "Cleaned Title is Empty"
        elif "keyword" in key:
            if value is None or len(value) <= 0:
                check = "Meta Keyword List is Empty"

    return check

def get_mongo_value(keyword, document):

    mongo_value = document.get(keyword)
    if isinstance(mongo_value, list):
        if len(mongo_value) > 0:
            mongo_value = document.get(keyword)
    elif isinstance(mongo_value, str):
        if mongo_value == "NULL":
            mongo_value = str(document.get(keyword)).strip()
        elif mongo_value != "None":
            mongo_value = str(document.get(keyword)).split('\"')
            for line in mongo_value:
                if line == "":
                    continue
                else:
                    mongo_value = line.strip()
                    break
    else:
        mongo_value = str(document.get(keyword)).strip()

    return mongo_value


def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

def path_step_back(path):
    path = str(path).split("/")
    path = '/'.join(path[:len(path)-1])
    if os.path.exists(path):
        return path
    else:
        return "Path Error!"

def load_configurations(config_file_name, app_name='bdm'):
    payload = {}

    dirname, filename = os.path.split(os.path.abspath(__file__))
    # print("dirname: {0}, filename: {1}".format(dirname, filename))
    path = path_step_back(dirname)
    file_path = os.path.join(path+'/', config_file_name)

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            make_json = ''.join(line for line in file if not line.startswith("#"))
            json_text = json.loads(make_json)

        payload = json_text.get(app_name)[0]
    else:
        raise IOError("File not found. Check Path!")

    return payload


if __name__ == '__main__':
    # print(date_finder(CONSTANTS.data_set4))
    print(is_connected())
