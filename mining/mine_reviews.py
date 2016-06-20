import os
import json
import simplejson
import pickle
import nltk
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder, TrigramCollocationFinder, TrigramAssocMeasures
from nltk.tag import pos_tag

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

def load_review_texts(file_name):
    if os.path.exists("products/{}.pickle".format(file_name)):
        data = open("products/{}.pickle".format(file_name), "r")
        reviews_texts_words = pickle.loads(data.read())
        data.close()
        return reviews_texts_words
    else:
        data = open("../crawler/{}.json".format(file_name), "r")
        json_ = json.loads(data.read())

        reviews_texts = "\n".join([r['reviewText'] for r in json_])
        reviews_texts_words = nltk.word_tokenize(reviews_texts)

        """tag POS"""
        reviews_texts_words = pos_tag(reviews_texts_words)

        """remove stopwords"""
        stop = nltk.corpus.stopwords.words('english')
        reviews_texts_words = [w for w in reviews_texts_words if w[0] not in stop]

        save = open("products/{}.pickle".format(file_name), "w")
        save.write(pickle.dumps(reviews_texts_words))
        save.close()
        return reviews_texts_words

def save_bigrams_data(file_name):
    """find bigram collocations"""
    raw_data = load_review_texts(file_name)
    raw_data = [(r[0].lower(), r[1]) for r in raw_data]

    bifinder = BigramCollocationFinder.from_words(raw_data)

    bi_pmi_scores = bifinder.score_ngrams(bigram_measures.pmi)
    bi_frequencies = dict(bifinder.ngram_fd.items())

    f = open("products/{}.json".format(file_name), 'w')
    bi_data = [{'w1':t[0][0], 'w2':t[0][1], 'pmi':t[1], 'fr':bi_frequencies[(t[0][0], t[0][1])]} for t in bi_pmi_scores]
    f.write(simplejson.dumps(sorted(bi_data, key=lambda x:x['fr']), indent=4))
    f.close()

"""trim results lower than n frequency and sort by pmi"""
def top_results(file_name, min_freq=1.0, num_res=14, allowed_pos=['NN'], sort_f=lambda x:x['pmi']):
    f = open("products/{}.json".format(file_name), 'r')
    data = json.loads(f.read())
    #min_freq = int(float(min_freq)/100*len(data))
    data = [d for d in data if int(d['fr']) > min_freq]
    data = [d for d in data if d['w1'][1] in allowed_pos and d['w2'][1] in allowed_pos]
    data = sorted(data, key=sort_f, reverse=True)
    f.close()
    return data[0:min(num_res, len(data))]

def pmi_freq_fitness(organism):
    files = ['amazon_fire', 'agents_of_shield', 'galaxys5']

    best = {'amazon_fire':['battery life',
                        'back button',
                        'sim card',
                        'screen protector',
                        'prime membership',
                        'pixel density',
                        'image stabilization',
                        'status bar',
                        'learning curve',
                        'gorilla glass',
                        'voice recognition',
                        'notification light',
                        'operating system',
                        'instant video'],
            'agents_of_shield':['edge seat',
                        'character development',
                        'story line',
                        'tv show'],
            'galaxys5':['finger print',
                        'fingerprint scanner',
                        'heart rate',
                        'rate monitor',
                        'sim card',
                        'water resistant',
                        'water resistance'
                        'charging port',
                        'home button',
                        'operating system',
                        'battery life']
        }

    """calculate fitness for an organism, an organism is (n0, n1, n2)"""
    results = {f:["%s %s" % (r['w1'][0], r['w2'][0]) for r in top_results(file_name=f, min_freq=organism[0], num_res=len(best[f]),
                                                                       sort_f=lambda x:float(organism[1])*x['pmi']+float(organism[2])*x['fr'])] for f in files}

    diffs = [list(set(best[f]) - set(results[f])) for f in files]

    return sum([len(d) for d in diffs])

if __name__ == '__main__':
    def get_terms(file_):
    	save_bigrams_data(file_)
    	res = top_results(file_)
	print "%s:" % file_
    	for w in res:
        	print "{0} {1} {2}".format(w['w1'][0], w['w2'][0], w['pmi'])

    get_terms('phones')
    get_terms('movies')
    get_terms('clothes')
