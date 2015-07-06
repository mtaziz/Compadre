import os
import json
import simplejson
import pickle
import nltk
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder, TrigramAssocMeasures
from nltk.tag import pos_tag

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

def load_review_texts(file_name):
    if os.path.exists("%s.pickle"%file_name):
        data = open("%s.pickle"%file_name, "r")
        reviews_texts_words = pickle.loads(data.read())
        data.close()
        return reviews_texts_words
    else:
        data = open("../crawler/%s.json"%file_name, "r")
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
        save = open("%s.pickle"%file_name, "w")
        save.write(pickle.dumps(reviews_texts_words))
        save.close()
        return reviews_texts_words

def save_bigrams_data(file_name):
    """find bigram collocations"""
    raw_data = load_review_texts(file_name)
    raw_data = [(r[0].lower(), r[1]) for r in raw_data]
    finder = BigramCollocationFinder.from_words(raw_data)

    """apply custom filter onto finder"""
    # finder.apply_freq_filter(int(1.0/100.0*6894.0))
    # results = finder.nbest(bigram_measures.pmi, 5)

    pmi_scores = finder.score_ngrams(bigram_measures.pmi)
    frequencies = dict(finder.ngram_fd.items())

    f = open('%s.json'%file_name, 'w')
    data = [{'w1':t[0][0], 'w2':t[0][1], 'pmi':t[1], 'fr':frequencies[(t[0][0], t[0][1])]} for t in pmi_scores]
    f.write(simplejson.dumps(sorted(data, key=lambda x:x['fr']), indent=4))
    f.close()

"""trim results lower than n frequency and sort by pmi"""
def top_results(file_name, min_freq=1.0, num_res=14, allowed_pos=['NN'], sort_f=lambda x:x['pmi']):
    f = open("%s.json"%file_name, 'r')
    data = json.loads(f.read())
    #min_freq = int(float(min_freq)/100*len(data))
    data = [d for d in data if int(d['fr']) > min_freq]
    data = [d for d in data if d['w1'][1] in allowed_pos and d['w2'][1] in allowed_pos]
    data = sorted(data, key=sort_f, reverse=True)
    f.close()
    return data[0:min(num_res, len(data)-1)]

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
    results = {f:["%s %s" % (r['w1'][0], r['w2'][0]) for r in top_results(file_name=f, min_freq=5, num_res=len(best[f]), 
                                                                       sort_f=lambda x:float(organism[1])*x['pmi']+float(organism[2])*x['fr'])] for f in files}

    diffs = [list(set(best[f]) - set(results[f])) for f in files]
    
    return sum([len(d) for d in diffs])

"""use genetic algorithm to optimize values of min_freq, and constants for pmi and fr"""
# from ga import run_ga
# run_ga(initial_pool=[(0.1, 1.0, 1.0), (0.1, 1.0, 2.0)], fitness=pmi_freq_fitness)
#run_ga(organisms_per_generation=10, cutoff=10, initial_pool=[], fitness=pmi_freq_fitness)



"""works?
top_results(min_freq="0.1%", sort_f=lambda x:x['pmi']*x['fr'])
"""
