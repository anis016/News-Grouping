from curses.ascii import isalnum

import common.utils as UTILS
import common.constants as CONSTANTS
import mongo.Mongo as MongoDB

import newspaper
import datefinder

import sys
import unicodedata
import re
import types


news_source = [
"http://www.spacedaily.com/reports/NASA_Electric_Research_Plane_Gets_X_Number_New_Name_999.html",
"http://www.prnewswire.com/news-releases/shrm-20-year-employee-benefits-trends-in-the-united-states--now-and-then-300286640.html",
"http://www.washingtontimes.com/news/2016/jun/20/company-to-donate-solar-energy-systems-to-7-waukeg",
"http://www.bloomberg.com/news/articles/2016-06-20/boeing-said-near-4-billion-deal-with-russian-firm-to-save-747",
"https://www.bostonglobe.com/business/2016/06/20/india-makes-easier-for-foreign-firms-invest-many-industries/GIzrXlcVBwFtPvCVwNknNM/story.html",
"http://www.marketwatch.com/story/djia-points-to-200-point-gain-as-polls-show-brexit-support-weakening-2016-06-20"
]

class ArticleScrape:

    def __init__(self):
        self.title = None
        self.description = None
        self.publish_date = None
        self.meta_keywords = []
        self.meta_description = None

    def __str__(self):
        return self.jsonify()

    def extract_text(self, source_news):

        article = newspaper.Article(source_news)
        article.download()
        article.parse()

        self.title = article.title
        self.description = article.text
        self.meta_keywords = article.meta_keywords
        self.meta_description = article.meta_description

        if article.publish_date is None:
            # Attempt to find the date
            UTILS.parse_date(article)
        else:
            self.publish_date = article.publish_date

        return self.jsonify()

    def __parse_metatags(self, source_news):
        pass

    def jsonify(self):
        # print("--------------------------------------------------")
        # print("Title: \n", )
        # print("Description: \n", article.text)
        # print("Published Date: \n", article.publish_date)
        # print("--------------------------------------------------")

        return {
            "title":            self.title,
            "description":      self.description,
            "publish_date":     self.publish_date,
            "meta_keywords":    self.meta_keywords,
            "meta_description": self.meta_description
        }


    # 1 Remove the white spaces, tabs, carriage return inbetween and from ends of each line
    def __remove_whitespace(self, line):
        remap = {
            ord('\t'): ' ',
            ord('\f'): ' ',
            ord('\r'): None
        }
        return re.sub('\s+', ' ', line.translate(remap))


    # 2 Normalize unicode data
    def __normalize_unicode(self, line):
        # cmb_chars = dict.fromkeys(ch for ch in range(sys.maxunicode) if unicodedata.combining(chr(ch)))
        b = unicodedata.normalize('NFD', line)
        return b.encode('ascii', 'ignore').decode('ascii')


    # 3 Remove the http: https: ftp: words
    def __remove_website(self, line):
        website = ["http:", "ftp:", "https:"]

        # res = ""
        # for st in line.split():
        #     if len([elem for elem in website if elem in st]) > 0:
        #         continue
        #     else:
        #         res += st + " "
        # return res

        # join is faster than concat
        return " ".join(str(st) for st in line.split() if len([elem for elem in website if elem in st]) <= 0)


    # 4 Remove the non-alphanumeric characters except the joining words and appostr
    def __remove_nonaplhanumer(self, line):
        st_list = re.compile(r"([a-zA-Z0-9]+(?:[-'’][a-zA-Z0-9]+)*)", re.UNICODE).split(line)

        # res = ""
        # for st in st_list:
        #     if check_alphanumer(st) is True:
        #         res += st + " "
        # return res.strip()
        return " ".join(str(st) for st in st_list if self.__check_alphanumer(st) is True).strip()

    def __check_alphanumer(self, data):
        for letter in data:
            if isalnum(letter):
                return True
        return False


    def clean_data(self, data):

        if isinstance(data, str) is False:
            raise TypeError

        rm_whitespace     = self.__remove_whitespace(data)
        normalize_unicode = self.__normalize_unicode(rm_whitespace)
        rm_website        = self.__remove_website(normalize_unicode)
        rm_nonaplhanumer  = self.__remove_nonaplhanumer(rm_website)

        print("cleaned: " + rm_nonaplhanumer + "\n")
        return rm_nonaplhanumer



news = ArticleScrape()

for src in news_source:
    json = news.extract_text(src)
    print(json.get("title"), "\n", json.get("publish_date"))
    # print(json.get("title"))
    # news.clean_data(json.get("title"))

# matches = datefinder.find_dates("WASHINGTON 20th June 2016")
# for match in matches:
#     print(match)