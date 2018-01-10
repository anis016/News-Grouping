# import sys
# print(sys.path)

from mongo.MongoDB import MongoDB
import csv
import os

import common.utils as utils
import common.constants as CONSTANTS

def path_step_back(path):
    path = str(path).split("/")
    path = '/'.join(path[:len(path)-1])
    if os.path.exists(path):
        return path
    else:
        return "Path Error!"

def path_reader(src_file):

    dirname, filename = os.path.split(os.path.abspath(__file__))
    path = path_step_back(dirname)

    file_path  = os.path.join(path + '/data/', src_file)
    if os.path.exists(file_path):
        return file_path
    else:
        print("Path Error")


def read_csv(src_file):
    csv_path = path_reader(src_file)

    ticker_dict = {}
    with open(csv_path, mode="r") as csv_file:
        readCSV = csv.reader(csv_file, delimiter=',')
        for row in readCSV:
            ticker = row[0]
            ticker_description = row[1]
            ticker_dict[ticker] = ticker_description

    return ticker_dict

def import_in_mongo(ticker_dict, mongoOb):
    stock_cursor = mongoOb.find(CONSTANTS.COLLECTION_STOCK)
    for document in stock_cursor:
        document_id = document.get("_id")
        document_Ticker = document.get("Ticker")
        description = ticker_dict.get(document_Ticker)
        print(description)

        mongoOb.update_one(CONSTANTS.COLLECTION_STOCK, {"_id": document_id}, {'description': description})


def main():
    mongoOb = MongoDB()
    mongoOb.initialzie()

    src_file = 'yahoo_ticker_symbols.csv'
    ticker_dict = read_csv(src_file)
    # print(ticker_dict)

    import_in_mongo(ticker_dict, mongoOb)

if __name__=='__main__':
    main()