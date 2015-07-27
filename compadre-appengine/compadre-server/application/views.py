import json
import yaml
import pprint

from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.ext import ndb

from flask import Flask, request, render_template, flash, url_for, redirect, session, g, jsonify
from application import app

from models import Item
from indexer import review_highlights_

app = Flask(__name__)

def index():
    return render_template("index.html")

def crawl_something(something):
    import json
    o = open('output.json', 'r')
    j = json.loads(o.read())

    for item in j:
        widgets = {}
        if item['widgets']['image_carousel']:
            widgets['image_carousel'] = item['widgets']['image_carousel']
        if item['widgets']['amazon_highlights']:
            widgets['review_highlights'] = review_highlights_(item['widgets']['amazon_highlights'])

        attributes = ""
        if item['']
        item_ = Item(name=item['name'][0], widgets=widgets, )
        item_.put()

def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
    """
    return ''
