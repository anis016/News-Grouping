# TF-IDF implementations
# tf-tdf(w) = tf(w) * idf(w)
# where, tf(w) = (Num. of times the word appears in a docs) / (Total Num. of words in the docs)
# idf(w) = log(Num. of docs / Num. of docs that contain word w)
import re
import os
from pprint import pprint

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords

def path_step_back(path):
    path = str(path).split("/")
    path = '/'.join(path[:len(path)-1])
    if os.path.exists(path):
        return path
    else:
        return "Path Error!"

def path_reader(src_file):

    src_dir    = os.getcwd()
    parent_dir = path_step_back(src_dir)

    file_path  = os.path.join(parent_dir + '/data/', src_file)
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


    def computeTF(self, wordDict, bow):
        tfDict = {}
        bowCount = len(bow)
        for word, count in wordDict.items():
            # bowCount: Total Num. of words in the docs
            # count   : Num. of times the word appears in a docs
            tfDict[word] = count / float(bowCount)
        return tfDict


    def computeIDF(self, docList):
        import math
        idfDict = {}
        N = len(docList)  # number of documents

        # count the number of documents that contain a word w
        idfDict = dict.fromkeys(docList[0].keys(), 0)
        for doc in docList:
            for word, value in doc.items():
                if value > 0:
                    idfDict[word] += 1

        # divide N by denominator above, take the log of that
        for word, value in idfDict.items():
            idfDict[word] = math.log(N / float(value))

        return idfDict

    def computeTFIDF(self, tfBow, idfs):
        tfidf = {}
        for word, value in tfBow.items():
            tfidf[word] = value * idfs[word]

        sorted_tfidf = sorted(tfidf.items(), key=lambda arg: arg[1], reverse=True)
        return sorted_tfidf

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
                    word_bags = self.separate_words(phrase)
                    tokenized_lists = tokenized_lists + word_bags
        return tokenized_lists

    def processTFIDF(self, all_docs):
        # calculate word-set
        tokenized_document = []
        for docs in all_docs:
            sentence_list = self.split_sentence(docs)
            tokenize_sentence = self.tokenize_document(sentence_list, self.stopwords_pattern)
            tokenized_document.append(tokenize_sentence)

        wordSet = set([word for document_list in tokenized_document for word in document_list])

        tfs = []
        all_wordDict = []
        for docs in tokenized_document:
            wordDict = dict.fromkeys(wordSet, 0)
            for word in docs:
                wordDict[word] += 1
            all_wordDict.append(wordDict)
            tfs.append(self.computeTF(wordDict, docs))

        idfs = self.computeIDF(all_wordDict)

        tfidf = []
        for tf in tfs:
            tfidf.append(self.computeTFIDF(tf, idfs))

        return tfidf

    def compute_keywords(self, all_docs):
        tfidf = self.processTFIDF(all_docs)
        pprint(tfidf)


if __name__ == '__main__':
    document_0 = "China has a strong economy that is growing at a rapid pace. However politically it differs greatly from the US Economy."
    document_1 = "At last, China seems serious about confronting an endemic problem: domestic violence and corruption."
    document_2 = "Japan's prime minister, Shinzo Abe, is working towards healing the economic turmoil in his own country for his view on the future of his people."
    document_3 = "Vladimir Putin is working hard to fix the economy in Russia as the Ruble has tumbled."
    document_4 = "What's the future of Abenomics? We asked Shinzo Abe for his views"
    document_5 = "Obama has eased sanctions on Cuba while accelerating those against the Russian Economy, even as the Ruble's value falls almost daily."
    document_6 = "Vladimir Putin is riding a horse while hunting deer. Vladimir Putin always seems so serious about things - even riding horses. Is he crazy?"

    all_documents = [document_0, document_1, document_2, document_3, document_4, document_5, document_6]

    tfidf = TFIDF()
    tfidf.compute_keywords(all_documents)