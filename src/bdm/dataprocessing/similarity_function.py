import collections
import math
from pprint import pprint

from rake import Rake
from tf_idf import TFIDF

# https://en.wikipedia.org/wiki/Jaccard_index
def jaccard_similarity(A, B):
    intersection = set(A).intersection(set(B))
    union        = set(A).union(set(B))
    return len(intersection)/len(union)

# https://en.wikipedia.org/wiki/Cosine_similarity
def cosine_similarity(A, B):
    dot_product = sum(p*q for p, q in zip(A, B))
    magnitude   = math.sqrt(sum([value**2 for value in A])) * math.sqrt(sum([value**2 for value in B]))
    if not magnitude:
        return 0
    return dot_product / magnitude

class DisjointSet(object):

    def __init__(self):
        self.leader = {} # maps a member to the group's leader
        self.group = {} # maps a group leader to the group (which is a set)

    def add(self, a, b):
        leadera = self.leader.get(a)
        leaderb = self.leader.get(b)
        if leadera is not None:
            if leaderb is not None:
                if leadera == leaderb: return # nothing to do
                groupa = self.group[leadera]
                groupb = self.group[leaderb]
                if len(groupa) < len(groupb):
                    a, leadera, groupa, b, leaderb, groupb = b, leaderb, groupb, a, leadera, groupa
                groupa |= groupb
                del self.group[leaderb]
                for k in groupb:
                    self.leader[k] = leadera
            else:
                self.group[leadera].add(b)
                self.leader[b] = leadera
        else:
            if leaderb is not None:
                self.group[leaderb].add(a)
                self.leader[a] = leaderb
            else:
                self.leader[a] = self.leader[b] = a
                self.group[a] = set([a, b])

if __name__ == '__main__':

    ######
    document_0 = "China has a strong economy that is growing at a rapid pace. However politically it differs greatly from the US Economy."
    document_8 = "China has a strong economy that is growing at a rapid pace. However politically it differs greatly from the US Economy."
    ######

    ######
    document_1 = "At last, China seems serious about confronting an endemic problem: domestic violence and corruption."
    ######

    ######
    document_2 = "Japan's prime minister, Shinzo Abe, is working towards healing the economic turmoil in his own country for his view on the future of his people."
    document_4 = "What's the future of Abenomics? We asked Shinzo Abe for his views"
    document_7 = "Japan's prime minister, Shinzo Abe, is working towards healing the economic turmoil in his own country for his view on the future of his people."
    #####

    #####
    document_5 = "Obama has eased sanctions on Cuba while accelerating those against the Russian Economy, even as the Ruble's value falls almost daily."
    #
    document_3 = "Vladimir Putin is working hard to fix the economy in Russia as the Ruble has tumbled."
    document_6 = "Vladimir Putin is riding a horse while hunting deer. Vladimir Putin always seems so serious about things - even riding horses. Is he crazy?"
    document_9 = "Vladimir Putin is working hard to fix the economy in Russia as the Ruble has tumbled."
    #####

    all_documents = [document_0, document_1, document_2, document_3, document_4, document_5, document_6, document_7, document_8, document_9]

    ###################################################################################################
    rake = Rake()
    keywords_group = collections.defaultdict(list)
    keywords_set = set()
    for id, document in enumerate(all_documents):
        extract_keywords = rake.compute_keywords(document)
        keywords_group[id] = [item for item in extract_keywords]
        for item in extract_keywords:
            keywords_set.add(item[0])

    # normalize
    result = collections.defaultdict(list)
    for docs in keywords_group.items():
        wordDict = dict.fromkeys(keywords_set, 0)
        id, keywords_score = docs
        for keywords, score in keywords_score:
            wordDict[keywords] = score
        result[id].append(wordDict)

    # pprint(result)

    dsRake = DisjointSet()
    for docs_id1, docs_score1 in result.items():
        for docs_id2, docs_score2 in result.items():
            if docs_id1 == docs_id2:
                continue
            docs_score1_value = list(docs_score1[0].values())
            docs_score2_value = list(docs_score2[0].values())

            similarity_score = cosine_similarity(docs_score1_value, docs_score2_value)

            if similarity_score > 0.1:
                dsRake.add(docs_id1, docs_id2)

    print("Using RAKE model")
    print(dsRake.group)
    ###################################################################################################

    tfidf = TFIDF()
    result = tfidf.compute_keywords(all_documents)
    # pprint(result)

    dsTFIDF = DisjointSet()
    for docs_id1, docs_score1 in result.items():
        for docs_id2, docs_score2 in result.items():
            if docs_id1 == docs_id2:
                continue
            docs_score1_value = list(docs_score1[0].values())
            docs_score2_value = list(docs_score2[0].values())

            similarity_score = cosine_similarity(docs_score1_value, docs_score2_value)

            if similarity_score > 0.1:
                dsTFIDF.add(docs_id1, docs_id2)

    print("Using VSM model")
    print(dsTFIDF.group)
    ###################################################################################################