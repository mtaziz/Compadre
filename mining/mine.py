import os
import json
import pickle
import nltk
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder, TrigramAssocMeasures
from nltk.tag import pos_tag

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

reviews_texts_words = ""

if os.path.exists("reviews_texts_words.txt"):
    data = open("reviews_texts_words.pickle", "r")
    reviews_texts_words = pickle.loads(data.read())
    data.close()
else:
    data = open("../crawler/reviews.json", "r")
    json_ = json.loads(data.read())

    print "tokenizing..."
    reviews_texts = [r['reviewText'] for r in json_]
    reviews_texts_words = nltk.word_tokenize("\n".join(reviews_texts))

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

print "finding collocations"
"""find bigram collocations"""
finder = BigramCollocationFinder.from_words(reviews_texts_words)
finder.apply_freq_filter(5) 
print finder.nbest(bigram_measures.pmi, 50)

