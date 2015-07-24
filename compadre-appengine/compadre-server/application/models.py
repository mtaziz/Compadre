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
    content = ndb.JsonProperty()

class Item(ndb.Model):
    """A database model for representing an individual product"""
    name = ndb.StringProperty(indexed=True)
    attributes = ndb.JsonProperty(indexed=False)
    widgets = ndb.JsonProperty(indexed=False) #[{"type":image_carousel, "data":[...], "dskey":"1234"}]
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












