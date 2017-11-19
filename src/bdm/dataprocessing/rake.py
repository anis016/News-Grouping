"""
Implementation of Rake Algorithm. (Chapter: 1)
Book: Text Mining Applications and Theory, by: Michael W. Berry, Jacob Kogan
"""
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


    def compute_keywords(self, text):
        sentence_list     = self.split_sentence(text)
        phrase_list       = self.generate_candidate_keywords(sentence_list, self.stopwords_pattern)
        word_scores       = self.calculate_word_scores(phrase_list)
        candidate_keyword = self.generate_candidate_keywords_score(phrase_list, word_scores)
        sorted_keywords = sorted(candidate_keyword.items(), key = lambda t: t[1] * -1)

        return sorted_keywords

if __name__ == '__main__':
    # text = '''The Waukegan School Board has approved a New Jersey company's $3 million donation of solar panels for seven school buildings. The (Lake County) News-Sun reports the project with NRG was delayed a year because of school officials’ concerns about the district’s liability if something happened to the equipment. A subcontractor will be required to meet standards the board demands. NRG spokesman David Gaier says the company plans to complete installation by the end of August with energy delivery beginning by year’s end. Gaier says each solar station will produce its own statistics about energy production, temperature, wind speed and more. NRG also supplies an energy-related curriculum for use in the classroom. School board vice president Rick Riddle is pleased with the educational opportunity provided.'''

    text = "WASHINGTON/SAN FRANCISCO (Reuters) - The U.S. Federal Reserves dwindling confidence in its own outlook and resulting confusion among investors are creating a policy problem that may require chief Janet Yellen to lay out her own views more forcefully. U.S. Federal Reserve Chair Janet Yellen holds a press conference following the Feds two-day Federal Open Market Committee (FOMC) policy meeting in Washington June 15, 2016. REUTERS/Kevin Lamarque The Fed chairs next communications test comes on Tuesday and Wednesday during her semi-annual testimony to U.S. lawmakers, less than a week after the central bank kept interest rates unchanged near record lows and lowered its projections for hikes in 2017 and 2018. A self-described consensus builder, Yellen sees her job as reflecting the whole committees views rather than setting an agenda for others to follow. I think thats a very laudable intent, but sometimes that produces a lack of clarity, said former Fed staffer and current partner at Cornerstone Macro LLC Roberto Perli. Sometimes there is a consensus for one reason and then next time there is a consensus for a different reason so the story shifts and people get confused. In fact, Fed policymakers deepening uncertainty about their own projections has resulted in the central bank sending mixed messages - repeatedly ratcheting up rate hike expectations only to tone them down later. COMMUNICATION BREAKDOWN At Wednesdays quarterly news conference Fed officials doubts were in plain view, with Yellen using the term uncertain or its variations 13 times, more than twice as often as in March. In December, when the Fed raised its rates by a quarter point for the first time in nearly a decade, that word only came up twice. And on Friday, James Bullard, a Fed voter this year, said the economy may need only one rate hike for the next two and half years, and called on the Fed to discard its long-run forecasts altogether, or risk losing credibility with markets. While most Fed officials still see two rate hikes this year, markets expect only one in December, if at all. (Graphic: tmsnrt.rs/28Jukri) This gap is a source of discomfort for Yellen who places a premium on making sure markets can anticipate how new economic data will guide the Feds decisions on rates. The Fed chief expressed surprise last week that markets had missed hints in the Feds April statement that a rate rise in June or July was possible and only got the message when the minutes of that meeting were published three weeks later. Federal Reserve Chair Janet Yellen speaks at the Radcliffe Institute for Advanced Studies at Harvard University in Cambridge, Massachusetts, U.S. May 27, 2016. REUTERS/Brian Snyder The Fed changed tack again barely two weeks later after Mays weak jobs report, the latest in a string of factors that have repeatedly forced the Fed to pause in its efforts to nudge interest rates further away from zero. The risk of data dependency is that it becomes data jumpiness, said JPMorgan economist Michael Feroli. TAKING THE LEAD Part of the reason for the Feds latest change in tune is its assessment of how high rates can rise before they start restraining economic growth. Last week, policymakers cut their projections for the third time in the last four quarterly projections. The level, now at 3 percent, is well below the 4.25 percent rate policymakers expected when they first began publishing long-term forecasts for the Feds policy rate in 2012. With a lower ceiling for rates, policymakers now expect a shallower path upward. Policymakers are also lowering their forecasts for those long-run rates more often. They cut their projections by 0.75 percentage points over the past year compared to a half a point cut over the prior three years. (Graphic: tmsnrt.rs/28JfmBR) Despite outliers, such as Bullard, whose views are at odds with the majority, the Fed appears to be coalescing around its latest forecasts. The central tendency ranges, which toss out the three highest and three lowest forecasts, show policymakers are projecting a narrower range of policy outcomes and economic indicators than they did in March, suggesting a majority is actually less divided over the right path for policy than just three months ago. The problem is investors and economists are still not clear what primarily shapes those views. The Feds 17 policymakers have stressed the importance of progress in employment and inflation and yet have repeatedly hit a pause button even as both indicators continue to improve. That is where Yellen, who is particularly concerned about labor market health, could create more clarity on what is now guiding the Fed by being more forthright with her personal views, Fed watchers say. Its weird for her to take part in that discussion and push things her way and yet then talk to the press about where the group is but not where she is, said Joe Gagnon, also a former Fed staffer and now senior fellow at the Peterson Institute for International Economics. She should probably be a bit more honest."
    rake = Rake()
    candidate_keywords = rake.compute_keywords(text)
    pprint(candidate_keywords)