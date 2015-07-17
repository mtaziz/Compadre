import logging
import requests
import json
import simplejson
import pprint
import yaml
from collections import OrderedDict
from lxml import html
from urllib import urlencode, unquote
from urlparse import urljoin, urlparse, parse_qsl, ParseResult

from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.selector import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

    def __init__(self, start_urls, item_template, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.items = []
        self.start_urls = start_urls
        self.item_template = item_template
        self.xpaths = {
            'blocks':'//div[@class="zg_itemImmersion"]',
            'small_img':'div[@class="zg_itemWrapper"]/div[@class="zg_image"]/div[@class="zg_itemImageImmersion"]/a//img/@src',
            'name':'//span[contains(@id, "Title")]/text()',
            'large_img':'//img[@id="landingImage"]/@src',
            'features':'//div[contains(@id, "feature-bullets")]//ul/li',
            'features_text':'descendant::*/text()[normalize-space() and not(ancestor::script | ancestor::style)]',
            'reviews':'//div[@class="a-section review"]',
            'review_id':'@id',
            'review_title':'div[2]/a[2]/text()',
            'review_text':'div[5]/span/text()',
            'review_stars':'div[2]/a[1]/i/span/text()',
            'reviews_max':'//ul[@class="a-pagination"]/li[last()-1]/a/text()',
            'url_reviews':'div[@class="zg_itemWrapper"]/div[@class="zg_reviews"]/span/a/@href',
            'url_description':'div[@class="zg_itemWrapper"]/div[@class="zg_title"]/a/@href'
        }

    def parse(self, response):
        sel = Selector(response)
        blocks = sel.xpath(self.xpaths['blocks'])

        for block in blocks:
            item = copy.deepcopy(self.item_template)
            item['widgets']['image_carousel'].extend(block.xpath(
                                                     self.xpaths['small_img']
                                                     ).extract())
            
            url_reviews = block.xpath(self.xpaths['url_reviews']
                                      ).extract()[0].strip()
            url_description = block.xpath(self.xpaths['url_description']
                                          ).extract()[0].strip()

            yield Request(url=url_description, meta={'item':item, 
                                                     'url_reviews':url_reviews}, 
                                                    callback=self.parse_description)
     
    def parse_description(self, response):
        sel = Selector(response)
        item = response.meta['item']
        url_reviews = response.meta['url_reviews']

        item['name'] = sel.xpath(self.xpaths['name']).extract()
        item['attributes'] = [''.join(f.xpath(self.xpaths('features_text'
                      )).extract()) for f in
                      sel.xpath(self.xpaths['features'])]
        item['widgets']['image_carousel'].extend(sel.xpath(
                                                 self.xpaths['large_img']
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
        max_ = int(sel.xpath(self.xpaths['reviews_max']).extract()[0])

        reviews = sel.xpath(self.xpaths['reviews'])

        for r in reviews:
            review = {}
            review['id'] = r.xpath(self.xpaths['review_id']).extract()[0]
            review['title'] = r.xpath(self.xpaths['review_title']).extract()[0]
            review['text'] = r.xpath(self.xpaths['review_text']).extract()[0]
            review['stars'] = r.xpath(self.xpaths['review_stars']).extract()[0]
            item['widgets']['amazon_highlights'].append(review)

        if next == max_:
            yield self.done(item)
        elif next < max_:
            yield Request(url=next_url(base_url, next), meta={
                                            'item': item,
                                            'next': next+1,
                                            'max': max_,
                                            'func': next_url,
                                            'base': base_url,
                                            }, 
                                            callback=self.parse_reviews)

    def done(self, item):
        """this function is necessary to break out of a generator when using
        yield -- can't yield and return in the same function"""
        return item