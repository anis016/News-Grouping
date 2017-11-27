# TF-IDF implementations
# tf-tdf(w) = tf(w) * idf(w)
# where, tf(w) = (Num. of times the word appears in a docs) / (Total Num. of words in the docs)
# idf(w) = log(Num. of docs / Num. of docs that contain word w)
import collections
import re
import os
from pprint import pprint

import math
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem.snowball import PorterStemmer

from similarity_function import cosine_similarity


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

def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False


def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    elif treebank_tag.startswith('S'):
        return wordnet.ADJ_SAT
    else:
        return wordnet.NOUN # default is NOUN

class TFIDF():

    def __init__(self):
        self.build_stopwords()

    def build_stopwords(self):
        # add nltk stopwords
        stopwords_lists = stopwords.words('english')

        # add more stopwords from the salton paper
        src_file = "stopwords.txt"
        file_path = path_reader(src_file)
        with open(file_path, "r") as file:
            for line in file:
                # remove the "\n" from end of the words
                if "\n" in line:
                    line = line.split("\n")
                if line not in stopwords_lists:
                    stopwords_lists.append(line[0])

        stop_word_regex_list = []
        for word in stopwords_lists:
            word_regex = r'\b' + word + r'(?![\w-])'  # added look ahead for hyphen
            stop_word_regex_list.append(word_regex)
        self.stopwords_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)


    def lemmatize_phrases(self, phrase):
        lemmatizer = WordNetLemmatizer()
        tokenize = [docs for docs in phrase.split(" ")]
        pos_word = nltk.pos_tag(tokenize)
        lemmatized_phrase_lists = []
        for word, pos in pos_word:
            tagged = get_wordnet_pos(pos)
            lemmatized_phrase_lists.append(lemmatizer.lemmatize(word, pos=tagged))
        return " ".join(lemmatized_phrase_lists)

    def stemming_phrases(self, phrase):
        porter_stemmer = PorterStemmer()
        tokenize = [docs for docs in phrase.split(" ")]
        stemmazied_phrase_lists = []
        for word in tokenize:
            stemmazied_phrase_lists.append(porter_stemmer.stem(word))
        return " ".join(stemmazied_phrase_lists)

    def term_frequency(self, term, tokenized_document):
        # The method count() returns the number of occurrences of substring
        # term in the string tokenized_document
        return tokenized_document.count(term)

    ## normalization: 1st way (log normalization)
    # tf(t, d) = 1 + log(f(t, d))
    def logarithmic_scaled_frequency(self, term, tokenized_document):
        counter = tokenized_document.count(term)
        # logarithmically scaled frequency: tf(t,d) = log ( 1 + ft,d), or zero if ft,d is zero;
        if counter == 0:
            return 0
        return 1 + math.log(counter)

    ## Calculate the IDF (Inverse Document Frequencies)
    # idf(t, D) = log(N/|{d is an element of D : t is an element of d}|)
    def inverse_document_frequencies(self, tokenized_documents):
        idf_values = {}
        all_tokens_set = set([item for sublist in tokenized_documents for item in sublist])
        for tkn in all_tokens_set:
            contains_token = map(lambda doc: tkn in doc, tokenized_documents)
            idf_values[tkn] = 1 + math.log(len(tokenized_documents) / (sum(contains_token)))
        return idf_values

    def split_sentence(self, text):
        """
        Splits the sentence based on the delimiters.
        :param text: the sentence
        :return: array of text after the split
        """
        sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
        sentences = sentence_delimiters.split(text)
        return sentences

    def separate_words(self, text):
        splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
        words = []
        for single_word in splitter.split(text):
            current_word = single_word.strip().lower()
            # leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
            if len(current_word) > 0 and current_word != '' and not is_number(current_word):
                words.append(current_word)
        return words

    def tokenize_document(self, sentence_list, stopwords_regex):
        tokenized_lists = []
        for sentence in sentence_list:
            tmp = re.sub(stopwords_regex, "|", sentence.strip())
            phrases = tmp.split("|")
            for phrase in phrases:
                phrase = phrase.strip().lower()
                if phrase != "":
                    # phrase = self.lemmatize_phrases(phrase)
                    phrase = self.stemming_phrases(phrase)
                    word_bags = self.separate_words(phrase)
                    tokenized_lists = tokenized_lists + word_bags
        return tokenized_lists

    def tfidf(self, documents):
        # break each document into list of tokenized document
        tokenized_documents = []
        for document in documents:
            sentence_list = self.split_sentence(document)
            tokenize_sentence = self.tokenize_document(sentence_list, self.stopwords_pattern)
            tokenized_documents.append(tokenize_sentence)

        # idf holds the set of the all the terms in the documents
        idf = self.inverse_document_frequencies(tokenized_documents)
        tfidf_documents = collections.defaultdict(list)
        for id, document in enumerate(tokenized_documents):
            dict_tfidf = {}
            # go through each of the terms in the idf and calculate the tf*idf value
            for term in idf.keys():
                tf = self.logarithmic_scaled_frequency(term, document)
                tfidf = tf * idf[term]
                dict_tfidf[term] = tfidf
            tfidf_documents[id].append(dict_tfidf)
        return tfidf_documents

    def compute_keywords(self, all_docs):
        tfidf = self.tfidf(all_docs)
        return tfidf

def flip(flag):
    if flag is True:
        return False
    else:
        return True

groups = collections.defaultdict(set)
group_value = 0

def transitive_closure(v1, v2):
    global group_value

    if len(groups) == 0:
        key = "group" + str(group_value)
        groups[key].add(v1)
        groups[key].add(v2)
        group_value += 1
    else:
        flagv1 = False
        flagv2 = False
        which_group = ""
        for key, value in groups.items():
            if v1 in value and v2 in value:
                which_group = key
                flagv2 = False
                flagv1 = False
                break
            elif v1 not in value and v2 in value:
                which_group = key
                flagv1 = True
                flagv2 = False
                break
            elif v1 in value and v2 not in value:
                which_group = key
                flagv1 = False
                flagv2 = True
                break
            elif v1 not in value and v2 not in value:
                flagv1 = True
                flagv2 = True

        if flagv1 == True and flagv2 == True:
            key = "group" + str(group_value)
            groups[key].add(v1)
            groups[key].add(v2)
            group_value += 1
        else:
            groups[which_group].add(v1)
            groups[which_group].add(v2)

if __name__ == '__main__':
    document_0 = "China has a strong economy that is growing at a rapid pace. However politically it differs greatly from the US Economy."
    document_1 = "At last, China seems serious about confronting an endemic problem: domestic violence and corruption."
    document_2 = "Japan's prime minister, Shinzo Abe, is working towards healing the economic turmoil in his own country for his view on the future of his people."
    document_3 = "Vladimir Putin is working hard to fix the economy in Russia as the Ruble has tumbled."
    document_4 = "What's the future of Abenomics? We asked Shinzo Abe for his views"
    document_5 = "Obama has eased sanctions on Cuba while accelerating those against the Russian Economy, even as the Ruble's value falls almost daily."
    document_6 = "Vladimir Putin is riding a horse while hunting deer. Vladimir Putin always seems so serious about things - even riding horses. Is he crazy?"
    document_7 = "Japan's prime minister, Shinzo Abe, is working towards healing the economic turmoil in his own country for his view on the future of his people."
    document_8 = "China has a strong economy that is growing at a rapid pace. However politically it differs greatly from the US Economy."
    document_9 = "Vladimir Putin is working hard to fix the economy in Russia as the Ruble has tumbled."

    all_documents = [document_0, document_1, document_2, document_3, document_4, document_5, document_6, document_7, document_8, document_9]


    tfidf = TFIDF()
    result = tfidf.compute_keywords(all_documents)
    # pprint(result)

    docs_comparision = []
    for docs_id1, docs_score1 in result.items():
        for docs_id2, docs_score2 in result.items():
            if docs_id1 == docs_id2:
                continue

            docs_score1_value = list(docs_score1[0].values())
            docs_score2_value = list(docs_score2[0].values())

            similarity_score = cosine_similarity(docs_score1_value, docs_score2_value)

            if similarity_score > 0.1:
                transitive_closure(docs_id1, docs_id2)
                docs_comparision.append((docs_id1, docs_id2))
    pprint(groups)
    print(docs_comparision)