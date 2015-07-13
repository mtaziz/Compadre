import logging
import requests
import json
from lxml import html
from urllib import urlencode, unquote
from urlparse import urljoin, urlparse, parse_qsl, ParseResult

from amazonbot.items import AmazonItem
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.selector import *

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
    start_urls = [
        "http://www.amazon.com/Best-Sellers-Electronics-Unlocked-Cell-Phones/zgbs/electronics/2407749011/ref=acs_ux_rw_ts_e_2407749011_more?pf_rd_p=2109755402&pf_rd_s=merchandised-search-5&pf_rd_t=101&pf_rd_i=2407749011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=176ZJ9DYYWYSZ2MW35GQ#1",
        "http://www.amazon.com/Best-Sellers-Electronics-Unlocked-Cell-Phones/zgbs/electronics/2407749011/ref=acs_ux_rw_ts_e_2407749011_more?pf_rd_p=2109755402&pf_rd_s=merchandised-search-5&pf_rd_t=101&pf_rd_i=2407749011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=176ZJ9DYYWYSZ2MW35GQ#2",
        "http://www.amazon.com/Best-Sellers-Electronics-Unlocked-Cell-Phones/zgbs/electronics/2407749011/ref=acs_ux_rw_ts_e_2407749011_more?pf_rd_p=2109755402&pf_rd_s=merchandised-search-5&pf_rd_t=101&pf_rd_i=2407749011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=176ZJ9DYYWYSZ2MW35GQ#3",
        "http://www.amazon.com/Best-Sellers-Electronics-Unlocked-Cell-Phones/zgbs/electronics/2407749011/ref=acs_ux_rw_ts_e_2407749011_more?pf_rd_p=2109755402&pf_rd_s=merchandised-search-5&pf_rd_t=101&pf_rd_i=2407749011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=176ZJ9DYYWYSZ2MW35GQ#4",
        "http://www.amazon.com/Best-Sellers-Electronics-Unlocked-Cell-Phones/zgbs/electronics/2407749011/ref=acs_ux_rw_ts_e_2407749011_more?pf_rd_p=2109755402&pf_rd_s=merchandised-search-5&pf_rd_t=101&pf_rd_i=2407749011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=176ZJ9DYYWYSZ2MW35GQ#5"
        ]

    def parse(self, response):
        sel = Selector(response)
        phones = sel.xpath('//div[@class="zg_itemImmersion"]')
        items = []

        for index,phone in enumerate(phones):
            item = AmazonItem()
            #item['name'] = phone.xpath('div[@class="zg_itemWrapper"]/div[@class="zg_title"]/a/text()').extract()[0]
            item['smallimg'] = phone.xpath('div[@class="zg_itemWrapper"]/div[@class="zg_image"]/div[@class="zg_itemImageImmersion"]/a//img/@src').extract()[0]
            
            reviews_url = phone.xpath('div[@class="zg_itemWrapper"]/div[@class="zg_reviews"]/span/a/@href').extract()[0]
            item_url = phone.xpath('div[@class="zg_itemWrapper"]/div[@class="zg_title"]/a/@href').extract()[0].strip()

            yield Request(url=item_url, meta={'item':item, 'reviews_url':reviews_url}, 
                          callback=self.get_details)
     
    def get_details(self, response):
        sel = Selector(response)
        item = response.meta['item']
        item['name'] = sel.xpath('//span[contains(@id, "Title")]/text()').extract()
        item['largeimg'] = sel.xpath('//img[@id="landingImage"]/@src').extract()
        item['features'] = sel.xpath('//div[contains(@id, "feature-bullets")]//ul/li/span/text()').extract()
        item['reviews'] = []

        yield Request(url=update_params(response.meta['reviews_url'], {'pageNumber':1}), 
                      meta={'item':item, 'curr_review_page':1, 
                      'num_review_page': None}, callback=self.get_reviews)

    def get_reviews(self, response):
        sel = Selector(response)
        item = response.meta['item']
        #logging.log(logging.INFO, "get_reviews url:{0}".format(response.url))
        curr_page = int(response.meta['curr_review_page'])
        num_pages = int(sel.xpath('//ul[@class="a-pagination"]/li[last()-1]/a/text()').extract()[0])

        reviews = sel.xpath('//div[@class="a-section review"]')

        for r in reviews:
            review = {}
            review['id'] = r.xpath('@id').extract()[0]
            review['title'] = r.xpath('div[2]/a[2]/text()').extract()[0]
            review['text'] = r.xpath('div[5]/span/text()').extract()[0]
            review['stars'] = r.xpath('div[2]/a[1]/i/span/text()').extract()[0]
            item['reviews'].append(review)

        if curr_page < num_pages-1:
            #scrape the next page of reviews
            yield Request(url=update_params(response.url, 
                          {'pageNumber':curr_page+1}), meta={'item':item,
            'curr_review_page':curr_page+1, 'num_review_page':num_pages},
            callback=self.get_reviews)
        elif curr_page < num_pages:
            yield Request(url=update_params(response.url, 
                          {'pageNumber':curr_page+1}), meta={'item':item,
            'curr_review_page':curr_page+1, 'num_review_page':num_pages},
            callback=self.get_reviews_done)

    def get_reviews_done(self, response):
        sel = Selector(response)
        item = response.meta['item']

        reviews = sel.xpath('//div[@class="a-section review"]')

        for r in reviews:
            review = {}
            review['id'] = r.xpath('@id').extract()[0]
            review['title'] = r.xpath('div[2]/a[2]/text()').extract()[0]
            review['text'] = r.xpath('div[5]/span/text()').extract()[0]
            review['stars'] = r.xpath('div[2]/a[1]/i/span/text()').extract()[0]
            item['reviews'].append(review)

        return item

"""
for dynamic stuff:
if there's a [a->b], have a function for that which crawls each url
one by one and passes the item with each call (like get_reviews)
"""






