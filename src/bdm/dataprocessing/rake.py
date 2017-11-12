"""
Implementation of Rake Algorithm. (Chapter: 1)
Book: Text Mining Applications and Theory, by: Michael W. Berry, Jacob Kogan
"""
import re
import os
import operator
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

def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False

class Rake():

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

    def split_sentence(self, text):
        """
        Splits the sentence based on the delimiters.
        :param text: the sentence
        :return: array of text after the split
        """
        sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
        sentences = sentence_delimiters.split(text)
        return sentences


    def lemmatize_phrases(self, phrase):
        lemmatizer = WordNetLemmatizer()
        tokenize = [docs for docs in phrase.split(" ")]
        pos_word = nltk.pos_tag(tokenize)
        lemmatized_phrase_lists = []
        for word, pos in pos_word:
            tagged = get_wordnet_pos(pos)
            lemmatized_phrase_lists.append(lemmatizer.lemmatize(word, pos=tagged))
        return " ".join(lemmatized_phrase_lists)


    def generate_candidate_keywords(self, sentence_list, stopwords_regex):
        phrase_lists = []
        for sentence in sentence_list:
            tmp = re.sub(stopwords_regex, "|", sentence.strip())
            phrases = tmp.split("|")
            for phrase in phrases:
                phrase = phrase.strip().lower()
                if phrase != "":
                    phrase = self.lemmatize_phrases(phrase)
                    phrase_lists.append(phrase)
        return phrase_lists

    def separate_words(self, text):
        splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
        words = []
        for single_word in splitter.split(text):
            current_word = single_word.strip().lower()
            # leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
            if len(current_word) > 0 and current_word != '' and not is_number(current_word):
                words.append(current_word)
        return words

    def build_co_occurance_graph(self, phrase_lists):
        word_frequency = {}
        word_degree = {}

        for phrase in phrase_lists:
            word_list        = self.separate_words(phrase)
            word_list_length = len(word_list)
            word_list_degree = word_list_length - 1

            for word in word_list:
                # initialize all word with 0
                word_frequency.setdefault(word, 0)
                word_degree.setdefault(word, 0)

                # if any occurance of words, then increase the counter
                word_frequency[word] += 1
                word_degree[word]    += word_list_degree

        for word in word_frequency:
            word_degree[word] = word_frequency[word] + word_degree[word]

        return {"frequency": word_frequency, "degree": word_degree}

    def calculate_word_scores(self, phrase_lists):
        frequency_degree_matrix = self.build_co_occurance_graph(phrase_lists)
        word_frequency = frequency_degree_matrix.get("frequency")
        word_degree    = frequency_degree_matrix.get("degree")

        word_score = {}
        # get each key and calculate the relative ratio
        for word in word_frequency:
            word_score.setdefault(word, 0)
            wd = word_degree.get(word)
            wf = word_frequency.get(word)
            word_score[word] = int(wd) / (int(wf) * 1.0)

        return word_score

    def generate_candidate_keywords_score(self, phrase_list, word_scores):
        candidate_keywords = {}
        for phrase in phrase_list:
            candidate_keywords.setdefault(phrase, 0)
            word_list = self.separate_words(phrase)
            candidate_score = 0
            for word in word_list:
                candidate_score += word_scores[word]
            candidate_keywords[phrase] = candidate_score
        return candidate_keywords


    def compute_keywords(self):
        sentence_list     = rake.split_sentence(text)
        phrase_list       = self.generate_candidate_keywords(sentence_list, self.stopwords_pattern)
        word_scores       = self.calculate_word_scores(phrase_list)
        candidate_keyword = self.generate_candidate_keywords_score(phrase_list, word_scores)
        sorted_keywords = sorted(candidate_keyword.items(), key = lambda t: t[1] * -1)

        return sorted_keywords

text = '''The Waukegan School Board has approved a New Jersey company's $3 million donation of solar panels for seven school buildings. The (Lake County) News-Sun reports the project with NRG was delayed a year because of school officials’ concerns about the district’s liability if something happened to the equipment. A subcontractor will be required to meet standards the board demands. NRG spokesman David Gaier says the company plans to complete installation by the end of August with energy delivery beginning by year’s end. Gaier says each solar station will produce its own statistics about energy production, temperature, wind speed and more. NRG also supplies an energy-related curriculum for use in the classroom. School board vice president Rick Riddle is pleased with the educational opportunity provided.'''

rake = Rake()
candidate_keywords = rake.compute_keywords()
pprint(candidate_keywords)