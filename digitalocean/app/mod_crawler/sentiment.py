"""function that analyzes sentiment about features in text by counting
occurences of common positive and negative words.
"""
def analyze_sentiment(sentence_words, features):
    """analyze sentiments expressed about product features in sentences"""
    positive_words = open('../datasets/positive-words.txt', 
                          'r').read().split('\n')
    negative_words = open('../datasets/negative-words.txt', 
                          'r').read().split('\n')

    #filter out features that aren't in the sentence
    features = [f for f in features if f in sentence_words]

    #assign words to features by proximity in sentence
    feature_scores = {f:0.0 for f in features}
    feature_words = {f:[] for f in features}

    #loop through each word and determine which feature it's closest to
    for i,w in enumerate(sentence_words):
        promixity_to_features = []
        for f in features:
            feature_occurrences = [i_ for i_,x in enumerate(sentence_words) 
                            if x == f]
            promixity_to_features.append((f, min([abs(i-o) for o in 
                                         feature_occurrences])))

        closest_feature = sorted(promixity_to_features, key=lambda x:x[1])[0][0]
        feature_words[closest_feature].append(w)

    #tally up sentiment scores
    for f in features:
        score = 0
        for w in feature_words[f]:
            if w in positive_words:
                score += 1
            elif w in negative_words:
                score -= 1
        feature_scores[f] = score

    return feature_scores




