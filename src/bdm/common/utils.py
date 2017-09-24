import datetime
from dateutil.parser import parse
import re

import newspaper
import datefinder

import common.constants as CONSTANTS

def convertTimeStampToDataTime(timeStamp):
    return datetime.datetime.fromtimestamp(int(timeStamp)).strftime("%Y-%m-%d")


def parse_date(article):
    meta_data = article.meta_data
    # parse dict
    publish_date = None
    for elem_key, elem_value in meta_data.items():
        if "date" in elem_key:
            if is_date(elem_value):
                publish_date = get_date(elem_value)
                return publish_date
        elif isinstance(elem_value, dict):
            for inner_elem_key, inner_elem_value in elem_value.items():
                if "date" in inner_elem_key:
                    if is_date(inner_elem_value):
                        publish_date = get_date(inner_elem_value)
                        return publish_date

    if publish_date is None:
        publish_date = date_finder(article.meta_description)
        if publish_date is not None:
            return publish_date.date()

def is_date(st):
    try:
        parse(st) # dateutil parser.parse
        return True
    except ValueError:
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
        if "body" in key:
            if value is None or len(value) <= 0:
                check = "Cleaned Body/Meta-Body is Empty"
        elif "title" in key:
            if value is None or len(value) <= 0:
                check = "Cleaned Title is Empty"
        elif "keyword" in key:
            if value is None or len(value) <= 0:
                check = "Meta Keyword List is Empty"

    return check


if __name__ == '__main__':
    print(date_finder(CONSTANTS.data_set4))