from curses.ascii import isalnum

import src.bdm.common.utils as UTILS
import src.bdm.common.constants as CONSTANTS
import src.bdm.common.errors as ERRORS
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib

import newspaper

import sys
import unicodedata
import re
import types

from src.bdm.common.utils import is_date_timestamp
from src.bdm.common.utils import is_connected

class ArticleScrape:

    def __init__(self):
        self.id = None
        self.title = None
        self.description = None
        self.publish_date = None
        # self.publish_date_found = None
        self.meta_keywords = []
        self.meta_description = None
        self.newsConnection = []
        self.stockConnection = []
        self.error = None

    def __str__(self):
        return self.jsonify()

    def clean_text(self, html):

        soup = BeautifulSoup(html, "lxml")  # create a new bs4 object from the html data loaded
        for script in soup(["script", "style", "head", "title", "meta", "[document]"]):  # remove all javascript and stylesheet code
            script.extract()
        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def get_keywords(self):

        keywords_list = []
        for keyword in self.meta_keywords:
            flag = False
            for letter in keyword:
                if isalnum(letter):
                    flag = True
                    break
            if flag == True:
                keywords_list.append(self.clean_data(keyword))

        return keywords_list

    def extract_text(self, source_news, publish_date, id=None):

        try:
            article = newspaper.Article(source_news)

            # code that checks if internet connection is present!
            # if not present stop the process

            if is_connected() is False:
                print("Internet Connection disrupted! Article's cannot be downloaded.")
                sys.exit(1)

            article.download()
            article.parse()

            self.id = id
            self.title = article.title
            self.description = article.text
            self.meta_keywords = article.meta_keywords
            self.meta_description = article.meta_description

            # this checks manually if there is any issue in self.meta_keywords
            keywords_list = self.get_keywords()

            if len(keywords_list) <= 0:
                self.meta_keywords = UTILS.parse_keywords(article)

            # soup = self.cleanMe(article.html)
            if self.description == "":
                self.description = self.clean_text(article.html)

            # Check if publish_date is a timestamp
            if is_date_timestamp(publish_date):
                self.publish_date = UTILS.convertTimeStampToDataTime(publish_date)
            elif article.publish_date is not None:
                self.publish_date = article.publish_date.date()
            else: # self.publish_date is None:
                self.publish_date = UTILS.parse_date(article)

            self.error = "False"

            return self.jsonify()

        except newspaper.ArticleException as err:
            self.id = id
            self.title = None
            self.description = None
            self.meta_keywords = []
            self.meta_description = None
            self.publish_date = publish_date

            self.error = "Article Exception"

            return self.jsonify()
        except Exception as err:
            self.id = id
            self.title = None
            self.description = None
            self.meta_keywords = []
            self.meta_description = None
            self.publish_date = publish_date

            # get the type of exception
            if article.download_exception_msg is not None:
                colon_len = article.download_exception_msg.find(":")
                self.error = article.download_exception_msg[:colon_len]
            else:
                self.error = "newspaper Exception"

            return self.jsonify()


    def jsonify(self):
        # print("--------------------------------------------------")
        # print("Title: \n", )
        # print("Description: \n", article.text)
        # print("Published Date: \n", article.publish_date)
        # print("--------------------------------------------------")

        return {
            "id":                 self.id,
            "title":              self.title,
            "description":        self.description,
            "publish_date":       self.publish_date,
            "meta_keywords":      self.meta_keywords,
            "meta_description":   self.meta_description,
            "error":              self.error
            # "publish_date_found": self.publish_date_found
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
        return " ".join(str(st) for st in line.split() if len([elem for elem in website if elem in st]) <= 0)


    # 4 Remove the non-alphanumeric characters except the joining words and appostr
    def __remove_nonaplhanumer(self, line):
        st_list = re.compile(r"([a-zA-Z0-9]+(?:[-'’/.][a-zA-Z0-9]+)*)", re.UNICODE).split(line)

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
        # rm_nonaplhanumer  = self.__remove_nonaplhanumer(rm_website)

        # print("cleaned: " + rm_nonaplhanumer + "\n")
        # return rm_nonaplhanumer

        return rm_website


if __name__ == "__main__":
    news = ArticleScrape()

    for src in CONSTANTS.news_source:
        json = news.extract_text(src)
        print(json.get("title"), "\n", json.get("publish_date"))