"""Each kind of item uses a kind of base spider to get its necessary data. 
For example, smartphones and laptops use the AmazonSpider. But Cars might use a different spider, 
because there might be a website that catalogs cars better than Amazon. smartphones and laptops also 
have reviews on Amazon, so it might be a good idea to crawl these reviews too, which is what the 
AmazonSpider does. Each item can have a series of widgets, or special views that are shown to the user, 
that rely on specific data. For instance, smartphones and laptops, and other items crawled from Amazon 
might take advantage of the ReviewHighlights Widget, which summarizes and scores review opinions, and 
extracts important features. Widgets on the front end (what the user sees) have a specific look, e.g. 
The ReviewHighlights widget is series of green and red sentences. The goal is to build a system where 
any combination of appropriate widgets and spiders can be created and added to any item. For instance, 
a ReviewHighlights widget should be added to any item that has reviews, whether it comes from Amazon or 
not (maybe it processes reviews on a cars website, which are scraped by a CarCrawler). In the Index file, 
each item is tied to a base spider, a series of urls, and a series of widgets. Items that are crawled by 
spiders that also crawl reviews for those items should use the ReviewHighlights widget, among other widgets. 
Each widget, or WidgetHandler, knows two things: 1. It knows how to access raw data given an item, and 2. 
It knows how to convert the raw data into something meaningful. For example, the ReviewHighlights widget 
should only be used for items who's Spiders crawl reviews, so its #1 is access Item['widgets']['review_highlights'], 
and its #2 is to use a series of mining functions to get the result. However, a different kind of widget, like a 
TwitterSentiment widget, knows how to process tweets. A base spider, like an AmazonSpider, builds an index or a 
list of items, which is necessary for building a database of content. Each item which wants a Twitter sentiment 
view, should use the TwitterSentiment widget, which invokes the TwitterSpider, which scrapes tweets about an 
item using its name. A TwitterSpider can't be used as a base spider, because it's built to collect tweets about 
1 item. The #1 for the TwitterSentiment is to invoke a TwitterSpider with the name of the item, and its #2 is 
to process the tweets in a certain way. The point of a base spider is to index a catalog of items which is 
searchable by users. Widgets and other non-base spiders are used to collect additional information about items, 
perhaps from other websites, that will be presented to the user. 
When the base spider scrapes the items, a pipeline saves them and adds them to a widget queue for processing.
"""

import yaml
from models import Item

# import scrapy
# from twisted.internet import reactor
# from scrapy.crawler import CrawlerProcess
# from scrapy.signalmanager import SignalManager
# from scrapy.utils.project import get_project_settings
# from spiders import AmazonSpider

import mining
import sentiment
import summarize

INDEX = "index.yaml"
ITEM_TEMPLATE = {
     "name":None,
     "attributes":None,
     "widgets":{}
}
SPIDERS = {
    'amazonspider': AmazonSpider
}
WIDGET_FUNCTIONS = {
    'image_carousel':'image_carousel_',
    'review_highlights':'review_highlights_'
}

# class ItemPipeline(object):

#     def process_item(self, item, spider):
#         """processes the widget data for each item and saves it to the
#         database"""
#         item_ = Item(name=item['name'],
#                      attributes=item['attributes'],
#                      widgets=item['widgets'],
#                      category=spider.class_name)
#         item_.put()


def get_index():
    index = yaml.load(open(INDEX,'r').read())
    return index

# def index_class(class_name):
#     """starts a spider with a callback to process widget data and 
#     save items to the database
#     """
#     index = get_index()
#     class_ = [c for c in index if c['name'] == class_name][0]
#     spider_name = class_['spider']
#     start_urls = class_['urls']
#     widgets = class_['widgets']

#     process = CrawlerProcess({
#         'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
#         'ITEM_PIPELINES': {'__main__.ItemPipeline': 1},
#     })   


#     process.crawl(AmazonSpider, start_urls=start_urls, item_template=ITEM_TEMPLATE, widgets=widgets, class_name=class_name)
#     process.start()

"""
the methods below are used to process raw data from crawls
and turn it into something meaningful
"""
def image_carousel_(images):
    return images

def review_highlights_(reviews):
    reviews_texts = " ".join([r['text'] for r in reviews])
    review_sentences = mining.to_sentences(reviews_texts)

    #pre-process text and find features
    review_words = mining.to_words(amazon_reviews)
    review_words = mining.pos_tag(review_words)
    review_words = [w for w in review_words if w[0] 
            not in mining.stopwords()]
    review_bigrams = mining.find_bigram_collocations(review_words)
    review_features = mining.amazon_features_from_collocations(
                review_bigrams)

    #find sentences that contain our features, summarize sentence groups
    #and score features for sentiment
    feature_sentences = {}
    feature_sentiments = {f:0 for f in amazon_features}

    for f in amazon_features:
        sentences = [s for s in review_sentences if f in s]
        cleaned_sentences = [mining.remove_stopwords(mining.to_words(s)) for s in sentences]
        #pick most central sentence
        central = summarize.rank_by_centrality(cleaned_sentences)
        feature_sentences[f] = sentences[central[0]]
        feature_sentiments[f] += sum([sentiment.analyze_sentiment(s, 
                                    amazon_features)[f] for s in sentences])
    content = {f:(feature_sentences[f], feature_sentiments[f])}

    return content