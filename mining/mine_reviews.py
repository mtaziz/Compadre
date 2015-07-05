import os
import json
import simplejson
import pickle
import nltk
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder, TrigramAssocMeasures
from nltk.tag import pos_tag

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

def load_review_texts():
    if os.path.exists("reviews_texts_words.pickle"):
        data = open("reviews_texts_words.pickle", "r")
        reviews_texts_words = pickle.loads(data.read())
        data.close()
        return reviews_texts_words
    else:
        data = open("../crawler/reviews.json", "r")
        json_ = json.loads(data.read())

        reviews_texts = "\n".join([r['reviewText'] for r in json_])

        print "tokenizing..."
        reviews_texts_words = nltk.word_tokenize(reviews_texts)

        print "tagging pos..."
        """tag POS"""
        reviews_texts_words = pos_tag(reviews_texts_words)

        print "removing stopwords..."
        """remove stopwords"""
        stop = nltk.corpus.stopwords.words('english')
        reviews_texts_words = [w for w in reviews_texts_words if w[0] not in stop]

        print "saving..."
        save = open("reviews_texts_words.pickle", "w")
        save.write(pickle.dumps(reviews_texts_words))
        save.close()
        return reviews_texts_words

def save_bigrams_data():
    """find bigram collocations"""
    finder = BigramCollocationFinder.from_words(load_review_texts())

    """apply custom filter onto finder"""
    # finder.apply_freq_filter(int(1.0/100.0*6894.0))
    # results = finder.nbest(bigram_measures.pmi, 5)

    pmi_scores = finder.score_ngrams(bigram_measures.pmi)
    frequencies = dict(finder.ngram_fd.items())

    f = open('bigram_scores.json', 'w')
    data = [{'w1':t[0][0], 'w2':t[0][1], 'pmi':t[1], 'fr':frequencies[(t[0][0], t[0][1])]} for t in pmi_scores]
    f.write(simplejson.dumps(sorted(data, key=lambda x:x['fr']), indent=4))
    f.close()

"""trim results lower than n frequency and sort by pmi"""
def top_results(min_freq=5, num_res=10, allowed_pos=['NN']):
    f = open('bigram_scores.json', 'r')
    data = json.loads(f.read())
    data = [d for d in data if d['fr'] >= min_freq]
    data = [d for d in data if d['w1'][1] in allowed_pos and d['w2'][1] in allowed_pos]
    data = sorted(data, key= lambda x:x['pmi'], reverse=True)
    f.close()
    return data[0:min(num_res, len(data)-1)]
    

