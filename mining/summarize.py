import networkx

def rank_by_centrality(tokenized_sentences):
    """Rank list of tokens by their centrality, by applying PageRank onto a 
    weighted graph of sentences
    """
    g = networkx.Graph()

    for i,s1 in enumerate(tokenized_sentences):
        for j,s2 in enumerate(tokenized_sentences):
            if not i == j:
                jc_sim = jaccard_similarity(tokenized_sentences[i], tokenized_sentences[j])
                g.add_edge(i, j, weight=jc_sim)
              
    pr = networkx.pagerank(g)
    ranked = sorted(list(pr.iteritems()), key=lambda x:x[1], reverse=True)
    return [r[0] for r in ranked]

def jaccard_similarity(tokens_a, tokens_b):
    return len(set(tokens_a).intersection(tokens_b)) / float(len(set(
        tokens_a).union(tokens_b)))