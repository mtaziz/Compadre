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
from app import db
import mining
import sentiment
import summarize

# class DataSource(ndb.Model):
#     """A database model for representing an individual DataSource.
#     A single item can have many sources of data.
#     """
#     content = ndb.JsonProperty()

# class Item(ndb.Model):
#     """A database model for representing an individual product"""
#     name = ndb.StringProperty(indexed=True)
#     attributes = ndb.JsonProperty(indexed=False)
#     widgets = ndb.JsonProperty(indexed=False) #[{"type":image_carousel, "data":[...], "dskey":"1234"}]
#     category = ndb.StringProperty(indexed=True)
#     date_added = ndb.DateTimeProperty(auto_now_add=True)

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

#Define an Item model
class Item(Base):

    __tablename__ = 'items'

    # User Name
    name    = db.Column(db.String(128),  nullable=False)

    # Identification Data: email & password
    email    = db.Column(db.String(128),  nullable=False,
                                            unique=True)
    password = db.Column(db.String(192),  nullable=False)

    # Authorisation Data: role & status
    role     = db.Column(db.SmallInteger, nullable=False)
    status   = db.Column(db.SmallInteger, nullable=False)

    # New instance instantiation procedure
    def __init__(self, name, email, password):

        self.name     = name
        self.email    = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.name)                      










