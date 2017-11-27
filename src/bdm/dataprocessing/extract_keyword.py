import re

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

from string import punctuation

import common.constants as CONSTANTS
from common.errors import Error
from common.utils import get_mongo_value
from mongo.MongoDB import MongoDB


def online_processing(document):
    pass

def main():

    mongoOb = MongoDB()
    mongoOb.initialzie()

    # news_cursor = mongoOb.find(CONSTANTS.COLLECTION_SUBSETNEWS)
    news_cursor = mongoOb.find(CONSTANTS.COLLECTION_SUBSETNEWS, {'id': '620'}) # for debugging purpose
    for document in news_cursor:
        mongo_id = str(document.get("id")).strip()
        cleaned_body      = get_mongo_value("cleaned_body", document)

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
