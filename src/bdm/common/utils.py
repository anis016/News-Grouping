import datetime
import newspaper

import dateparser
import datefinder
import semantic

def convertTimeStampToDataTime(timeStamp):
    return datetime.datetime.fromtimestamp(int(timeStamp)).strftime("%Y-%m-%d %H:%M:%S")

def parse_date(article):
    meta_data = article.meta_data
    for
    pass
    #  = article.meta_description
    # datetime = DateService.extractDates(meta_description)

def normalize_date(line):
    pass