import datetime
import newspaper

import dateparser
import datefinder
import semantic

def convertTimeStampToDataTime(timeStamp):
    return datetime.datetime.fromtimestamp(int(timeStamp)).strftime("%Y-%m-%d %H:%M:%S")

def parse_date(article):
    meta_data = article.meta_data
    # parse dict
    pass
    #  = article.meta_description
    # datetime = DateService.extractDates(meta_description)

data_set = '''
'Washington DC (SPX) Jun  - 
With 14 electric motors turning propellers and all of them integrated into a uniquely-designed wing, NASA will test new propulsion technology using an experimental airplane now designated the X-57 a'
'''

def date_finder(st):
    matches = datefinder.find_dates(st)
    for match in matches:
        print(match)

def normalize_date(line):
    pass
