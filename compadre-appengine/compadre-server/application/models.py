"""A property in Item that needs to be scraped from the web, like its attributes,
or its amazon reviews highlights, is stored as a DataSource. This DataSource
provides a url, and crawling instructions, which are to be carried out by a
cron job. This cron job will do two things: (1) scan the DataSource table to
look for DataSource(s) that haven't been crawled in a while, or at all, and
crawl them. And (2) take the crawled information, do something with its content,
and store the result in the content field of the DataSource. For instance, if a
DataSource has data_type "amazon-reviews", then the script in the cron job
should, after it's done crawling as per the instructions, extract the bigram
features from the review sentences, pick the most central sentences for each
feature and get an average sentiment score for the feature, then save this
information as a json-serialized dict in the "content" field of the DataSource,
so that the Item can be displayed, etc. This is achievied with a variety of
classes, like AmazonReviewsDataSource, which can process crawled data to
its final form, and a crawler mixin, which can crawl the information.
"""
from google.appengine.ext import ndb

import mining
import sentiment
import summarize
from crawler import sort_od, crawl

class DataSource(ndb.Model):
    """A database model for representing an individual DataSource.
    A single item can have many sources of data.
    """
    data_type = ndb.StringProperty(indexed=True)
    content = ndb.JsonProperty(indexed=True)
    crawl_instructions = ndb.JsonProperty(indexed=False)
    crawl_date = ndb.DateTimeProperty(indexed=False) 

class Item(ndb.Model):
    """A database model for representing an individual product"""
    name = ndb.StringProperty(indexed=True)
    attributes = ndb.JsonProperty(indexed=False)
    images = ndb.JsonProperty(indexed=False)
    data_sources = ndb.JsonProperty(indexed=False) #list of DataSource keys
    category = ndb.StringProperty(indexed=True)
    date_added = ndb.DateTimeProperty(auto_now_add=True)

class CrawlableMixin():
    """A mixing enabling DataSource classes to crawl the web"""

    def crawl_(self, crawl_instructions):
        """run the crawler and carry out the instructions"""

        instructions = sort_od(crawl_instructions)
        result = crawl(sort_od(crawl_data))

        final_result = []

        #combine duplicates
        unique_field = [k for k in result[0].keys() if "*" in k][0]

        for r in result:

            dupe = [final_result.index(f) for f in final_result 
                if r[unique_field] == f[unique_field]]

            if dupe:
                dupe = dupe[0]
                for k,v in r.iteritems():
                    if not v == final_result[dupe][k]:
                        if isinstance(final_result[dupe][k], list):
                            final_result[dupe][k].append(v)
                        else:
                            final_result[dupe][k] = [final_result[dupe][k], v]
            else:
                final_result.append(r)

        return final_result

class AmazonReviewsDataSource(CrawlableMixin, DataSource):
    """A class for managing a DataSource that processes amazon reviews into 
    summary sentences with sentiment scores.
    """    
    def process_content():
        crawl_result = self.crawl_( self.crawl_instructions )
        amazon_reviews = " ".join([r['reviewText'] for r in crawl_result])
        review_sentences = mining.to_sentences(amazon_reviews)

        #pre-process text and find features
        review_words = mining.to_words(amazon_reviews)
        review_words = mining.pos_tag(review_words)
        review_words = [w for w in review_words if w[0] 
                not in mining.stopwords()]
        review_bigrams = mining.find_bigram_collocations(review_words)
        amazon_features = mining.amazon_features_from_collocations(
                    review_bigrams)

        #find sentences that contain our features, summarize sentence groups
        #and score features for sentiment
        feature_sentences = {}
        feature_sentiments = {f:0 for f in amazon_features}

        for f in amazon_features:
            sentences = [s for s in review_sentences if f in s]
            cleaned_sentences = [mining.remove_stopwords(mining.to_words(s) 
                                                         for s in sentences]
            #pick most central sentence
            central = summarize.rank_by_centrality(cleaned_sentences)
            feature_sentences[f] = sentences[central[0]]
            feature_sentiments[f] += sum([sentiment.analyze_sentiment(s, 
                                        amazon_features)[f] for s in sentences])

        #update object in database
        content = json.dumps({f:(feature_sentences[f], feature_sentiments[f])})
        self.content = content
        self.put()
















