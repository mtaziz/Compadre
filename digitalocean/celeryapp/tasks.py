from __future__ import absolute_import
import logging
from celeryapp.celery import app

@app.task
def scrape(process, index, class_name, spider_name, start_urls, widgets): 
    logging.log(logging.INFO, "scrape celery task running")
    process.crawl(spider_name, start_urls=start_urls, 
                  item_template=ITEM_TEMPLATE, widgets=widgets, 
                  class_name=class_name)
    process.start()