import nltk
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder, TrigramAssocMeasures
from nltk.tag import pos_tag
from summarize import rank_by_centrality
from sentiment import feature_scores

def to_words(sentence):
    """Given some text, return a list of words"""
    return nltk.word_tokenize(sentence)

def to_sentences(text):
    """Given some text, return a list of sentences"""
    return nltk.sent_tokenize(text)

def to_tokenized_sentences(text):
    """Given some text, return a list of tokenized sentences"""
    return [to_words(s) for s in to_sentences(text)]

def stopwords():
    return nltk.corpus.stopwords.words('english')

def remove_stopwords(words):
    """Given a list of words, return the list without stopwords"""
    stop = nltk.corpus.stopwords.words('english')
    return [w for w in words if w not in stop]

def pos_tag_(words):
    """tag parts of speech of words"""
    return pos_tag(reviews_texts_words)

def find_bigram_collocations(words):
    finder = BigramCollocationFinder.from_words(words)
    pmi_scores = finder.score_ngrams(bigram_measures.pmi)
    frequencies = dict(finder.ngram_fd.items())

    collocations = [{'w1':t[0][0], 
            'w2':t[0][1], 
            'pmi':t[1], 
            'fr':frequencies[(t[0][0], 
                              t[0][1])] } for t in pmi_scores]

    return collocations

def amazon_features_from_collocations(collocations, num_results=10, allowed_pos=['NN']):
    """extract features from amazon reviews"""
    min_frequency  = 5.0
    pmi_weight     = 0.3135673133977043
    freq_weight    = 0.0048902107342438

    #filter and sort collocations
    collocations = [c for c in collocations if (c['w1'][1] in allowed_pos 
                                                and c['w2'][1] in allowed_pos)]
    collocations = [c for c in collocations if int(c['fr']) > min_frequency]
    collocations = sorted(collocations, key=lambda x: pmi_weight*x['pmi'] + freq_weight*x['fr'], reverse=True)
    collocations_top = collocations[0:min(num_results, len(collocations)

    return ["{0} {1}".format(coll['w1'], coll['w2']) for coll in collocations_top]











