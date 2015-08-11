from __future__ import absolute_import
import logging
from celeryapp.celery import app

class ItemPipeline(object):

    def process_item(self, item, spider):
        """processes the widget data for each item and saves it to the
        database"""
        print "saving {}".format(item['name'])
        # item_ = Item(name=item['name'],
        #              attributes=item['attributes'],
        #              widgets=item['widgets'],
        #              category=spider.class_name)104.236.177.107
        # item_.put()

@app.task
def scrape(class_name, spider_name, start_urls, widgets):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'ITEM_PIPELINES': {'__main__.ItemPipeline': 1},
    })

    logging.log(logging.INFO, "scrape celery task running")
    process.crawl(spider_name, start_urls=start_urls, 
                  item_template=ITEM_TEMPLATE, widgets=widgets, 
                  class_name=class_name)
    process.start()