import os
import copy
import logging
import requests
import json
import yaml
from lxml import html
from urllib import urlencode, unquote
from urlparse import urljoin, urlparse, parse_qsl, ParseResult

from amazonbot.items import AmazonItem
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request, Response, HtmlResponse
from scrapy.selector import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#import simplejson; open('output_pretty.json', 'w').write( simplejson.dumps(simplejson.loads(open('output.json', 'r').read()), indent=4, sort_keys=True) );exit()

chromedriver = "/Users/yonatanoren/Documents/Projects/Comparisto/crawler/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

item_template = {
     "name":None,
     "attributes":None,
     "widgets":{"image_carousel":[], "amazon_highlights":[]}
}

xpaths = {
    'small_img':'div[@class="zg_itemWrapper"]/div[@class="zg_image"]/div[@class="zg_itemImageImmersion"]/a/img/@src',
    'name':'//span[contains(@id, "Title")]/text()',
    'large_img':'//img[@id="landingImage"]/@src',
    'features':'//div[contains(@id, "feature-bullets")]//ul/li',
    'reviews':'//div[@class="a-section review"]',
    'review_id':'@id',
    'review_title':'div[2]/a[2]/text()',
    'review_text':'div[5]/span/text()',
    'review_stars':'div[2]/a[1]/i/span/text()',
    'reviews_max':'//ul[@class="a-pagination"]/li[last()-1]/a/text()',
    'url_reviews':'div[@class="zg_itemWrapper"]/div[@class="zg_reviews"]/span/a/@href',
    'url_description':'div[@class="zg_itemWrapper"]/div[@class="zg_title"]/a/@href',
    'pagination':'//li[@class="zg_page zg_selected"]'
}

def update_params(url, params):
    """
    Taken from:
    http://stackoverflow.com/questions/2506379/add-params-to-given-url-in-python
    """
    url = unquote(url)
    parsed_url = urlparse(url)
    get_args = parsed_url.query
    parsed_get_args = dict(parse_qsl(get_args))
    parsed_get_args.update(params)

    parsed_get_args.update(
        {k: dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    encoded_get_args = urlencode(parsed_get_args, doseq=True)

    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url

class AmazonSpider(Spider):
    name = "amazon"
    allowed_domains = ['amazon.com']
    
    def __init__(self, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.start_urls = ["http://www.amazon.com/Best-Sellers-Electronics-Contract-Cell-Phones/zgbs/electronics/2407747011/ref=zg_bs_2407747011_pg_2?_encoding=UTF8&pg=2"]
        self.items = []
        self.driver = webdriver.Chrome(chromedriver)
    
    def parse(self, response):
        #wait for amazon to paginate
        self.driver.get(response.url)
        logging.log(logging.INFO, "WAITING FOR PAGINATION")
        page_selected = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpaths['pagination']))
            )
        logging.log(logging.INFO, "PAGINATION DONE")
        #reset response with updated page
        response = HtmlResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
        sel = Selector(response)
        blocks = sel.xpath('//div[@class="zg_itemImmersion"]')

        for i,block in enumerate(blocks):
            item = copy.deepcopy(item_template)
            images = block.xpath(xpaths['small_img']).extract()
            item['widgets']['image_carousel'].extend(block.xpath(
                                                     xpaths['small_img']
                                                     ).extract())
            
            url_reviews = block.xpath(xpaths['url_reviews']
                                      ).extract()[0].strip()
            url_description = block.xpath(xpaths['url_description']
                                          ).extract()[0].strip()

            yield Request(url=url_description, meta={'item':item, 
                                                     'url_reviews':url_reviews}, 
                                                    callback=self.parse_description)
        self.driver.close()
     
    def parse_description(self, response):
        sel = Selector(response)
        item = response.meta['item']
        url_reviews = response.meta['url_reviews']

        item['name'] = sel.xpath(xpaths['name']).extract()
        item['attributes'] = ["".join(f.xpath("descendant::*/text()[normalize-space() and not(ancestor::script | ancestor::style)]").extract())
                        for f in sel.xpath(xpaths['features'])]
        item['widgets']['image_carousel'].extend(sel.xpath(
                                                 xpaths['large_img']
                                                 ).extract())

        next_url = lambda base_url, next: update_params(base_url, 
                                                        {'pageNumber':next})

        yield Request(url=next_url(url_reviews, 1), meta={
                                                    'item': item,
                                                    'next': 2,
                                                    'max': None,
                                                    'func': next_url,
                                                    'base': url_reviews,
                                                    }, 
                                                    callback=self.parse_reviews)
    def parse_reviews(self, response):
        sel = Selector(response)
        item = response.meta['item']

        next_url = response.meta['func']
        base_url = response.meta['base']
        next = int(response.meta['next'])
        max_ = 1#int(sel.xpath(xpaths['reviews_max']).extract()[0])

        reviews = sel.xpath(xpaths['reviews'])

        for r in reviews:
            review = {}
            review['id'] = r.xpath(xpaths['review_id']).extract()[0]
            review['title'] = r.xpath(xpaths['review_title']).extract()[0]
            review['text'] = r.xpath(xpaths['review_text']).extract()[0]
            review['stars'] = r.xpath(xpaths['review_stars']).extract()[0]
            item['widgets']['amazon_highlights'].append(review)

        logging.log(logging.INFO, "next:%s max:%s" % (next, max_))

        if next < max_:
            yield Request(url=next_url(base_url, next), meta={
                                            'item': item,
                                            'next': next+1,
                                            'max': max_,
                                            'func': next_url,
                                            'base': base_url,
                                            }, 
                                            callback=self.parse_reviews)
        else:
            yield self.done(item)

    def done(self, item):
        """this function is necessary to break out of a generator when using
        yield -- can't yield and return in the same function"""
        return item




"""
for dynamic stuff:
if there's a [a->b], have a function for that which crawls each url
one by one and passes the item with each call (like get_reviews)
"""






