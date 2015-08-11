from __future__ import absolute_import

from celeryapp.celery import app

@app.task
def scrape(process, index, class_name, spider_name, start_urls, widgets): 
    process.crawl(spider_name, start_urls=start_urls, 
                  item_template=ITEM_TEMPLATE, widgets=widgets, 
                  class_name=class_name)
    process.start()