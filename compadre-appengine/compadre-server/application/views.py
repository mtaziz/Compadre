import json
import yaml
import pprint

from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.ext import ndb

from flask import Flask, request, render_template, flash, url_for, redirect, session, g, jsonify
from application import app

import models

app = Flask(__name__)

def index():
    return render_template("index.html")

def crawler_worker()
def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
    """
    return ''
