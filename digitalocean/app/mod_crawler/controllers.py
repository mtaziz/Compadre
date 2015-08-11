from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db

import indexer

mod_crawler = Blueprint('crawler', __name__, url_prefix='/crawler')

@mod_crawler.route('/crawl/<classname>/', methods=['GET', 'POST'])
def crawl(classname):
    print classname
    indexer.index_class(classname)
