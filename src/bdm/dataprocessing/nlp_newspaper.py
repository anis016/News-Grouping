import pandas as pd
import numpy as np

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

from mongo.MongoDB import *
import common.constants as CONSTANTS
from common.utils import *

import os
import sys
from string import punctuation

class ArticleNLP:

    def __init__(self):
        self.stopwords = set(stopwords.words('english'))

        self.title_keywords = []
        self.descr_keywords = []

    # break the descriptions into sentences and then break the sentences into tokens
    # remove punctuation and stop words
    # lowercase the tokens
    def tokenizer(self, text):
        # text = "US stocks close-higher as Brexit-98 worries wane's"
        try:
            tokens_ = [word_tokenize(sent) for sent in sent_tokenize(text)]

            tokens = []
            for token_by_sent in tokens_:
                tokens += token_by_sent

            tokens = list(filter(lambda t: t.lower() not in self.stopwords, tokens))
            tokens = list(filter(lambda t: t not in punctuation, tokens))
            tokens = list(filter(lambda t: t not in [u"'s", u"n't", u"...", u"''", u'``', u'\u2014', u'\u2026', u'\u2013'], tokens))

            filtered_tokens = []
            for token in tokens:
                if re.search('[a-zA-Z]', token):
                    filtered_tokens.append(token)

            filtered_tokens = list(map(lambda token: token.lower(), filtered_tokens))

            return filtered_tokens

        except Error as e:
            print(e)

def main():
    nlp = ArticleNLP()

    mongoOb = MongoDB()
    mongoOb.initialzie()

    # news_cursor = mongoOb.find(CONSTANTS.COLLECTION_SUBSETNEWS)
    news_cursor = mongoOb.find(CONSTANTS.COLLECTION_SUBSETNEWS, {'id': '620'}) # for debugging purpose
    for document in news_cursor:
        mongo_id = str(document.get("id")).strip()
        cleaned_title     = get_mongo_value("cleaned_title", document)
        cleaned_body      = get_mongo_value("cleaned_body", document)
        cleaned_metabody  = get_mongo_value("cleaned_metabody", document)

        tokenize_title    = nlp.tokenizer(cleaned_title)
        tokenize_body     = nlp.tokenizer(cleaned_body)
        tokenize_metabody = nlp.tokenizer(cleaned_metabody)

        # Calculate TF-IDF
        # https://stackoverflow.com/questions/36966019/how-aretf-idf-calculated-by-the-scikit-learn-tfidfvectorizer#answer-36972265
        # http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

        vectorizer = TfidfVectorizer(max_df=0.2,
                                     tokenizer=nlp.tokenizer,
                                     ngram_range=(1, 3))
        vz = vectorizer.fit_transform(list(cleaned_title))
        print(vz.shape)

        feautre_names = vectorizer.get_feature_names()
        for feature in feautre_names:
            print(feature)

if __name__ == '__main__':
    main()
