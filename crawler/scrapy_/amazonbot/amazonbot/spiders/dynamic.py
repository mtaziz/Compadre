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

def sort_od(od):
    """sort the resulting dictionary so that we evaluate the urls last. 
    New urls have nested attributes that are dependent on new pages, so we need
    to finish gathering all of the data associated with a current page before 
    moving onto a new one.
    """
    res = OrderedDict()
    for k, v in sorted(od.items(), key=lambda x: (1 if isinstance(x[1], 
                       dict) else 0)):
        if isinstance(v, dict):
            res[k] = sort_od(v)
        else:
            res[k] = v
    return res

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

class DynamicSpider(Spider):
    name = "DynamicSpider"
    allowed_domains = ["*"]
    
    """
    need items = []
    can use yield
    DynamicItem() not necessary
    """

    def __init__(self, *args, **kwargs):
        super(DynamicSpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        self.items = []
 
        #load instruction set
        instructions = """
        http://www.amazon.com/Best-Sellers-Electronics-Unlocked-Cell-Phones/zgbs/electronics/2407749011/ref=acs_ux_rw_ts_e_2407749011_more?pf_rd_p=2109755402&pf_rd_s=merchandised-search-5&pf_rd_t=101&pf_rd_i=2407749011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=176ZJ9DYYWYSZ2MW35GQ#[1->5]:
            items: 
                //div[@class="zg_itemImmersion"]:
                    img1: div[@class="zg_itemWrapper"]/div[@class="zg_image"]/div[@class="zg_itemImageImmersion"]/a//img/@src
                    url->div[@class="zg_itemWrapper"]/div[@class="zg_title"]/a/@href:
                        name: //span[contains(@id, "Title")]/text()
                        img2: //img[@id="landingImage"]/@src
                        features: //div[contains(@id, "feature-bullets")]//ul/li/span/text()       
                    reviews:
                        url->div[@class="zg_itemWrapper"]/div[@class="zg_reviews"]/span/a/@href[pageNumber 1->1]:
                            reviewId*: //div[@class="a-section review"]/@id
                            reviewTitle: //div[@class="a-section review"]/div[2]/a[2]/text()
                            reviewText: //div[@class="a-section review"]/div[5]/span/text()
                            reviewStars: //div[@class="a-section review"]/div[2]/a[1]/i/span/text()
        """

        """
        for the first non var:xpath
        def chain_requests:
            meta : {
                item: item,
                instructions:iteritems() #carry a generator
            }

            
            k,v = instructions.next()

            if v is not a dict:
                item[k] = sel.xpath(v)
            if k is a url:
                yield Request(url=k, meta={item:item, instructions:instructions, inner:v.iteritems()}
            if k is a var:
                if v.keys[0] is a url:
                    yield Request(url=k, meta={item:item, instructions:instructions, inner:v.iteritems()})

            
            chain requests with passing a variable, and when we reach the end of the urls/blocks,
            set the item's property to the result.
            if there is nothing left in next, return the item,
            otherwise 


        #happens in parse()
        we've reached dict with key "items", so k=items:
            
            blocks = sel.xpath(v
            for b in blocks:
                item = {}
                #get all the values
                #loop through k,vs and stop at the first url/dict 
                for 
                yield handle_block(b, meta={"item":item, "next":OrderedDict(dict.iteritems() })

        def handle_block(self, block, meta={"item":item, "next":next_instructions })
            item = meta['item']
            next = meta['next']
            for k,v in next.iteritems():
                        if v is not a dict then item[k] = block.xpath(k)
                        if v is a dict and k is a url: 

            if (reached end):
                return item

        def handle_urls(self, response, meta={"urls":urls})


        def chain_requests()
        """
        

        """
        rules:
        if v is xpath and k is a variable name, item[var] = sel.xpath().extract()
        if v is a dict and k is "items", yield Request(callback=self.crawl)
        if v is a dict and k is a variable name, item[var] = crawl(v)
        if v is a dict and k is an xpath block:
            loop through all instances of xpath and yield crawl(v)
            with item and v in meta
        if v is a dict and k is an xpathurl:
            urls = get_urls(page.xpath(xpathurl))
            return crawl_chain(url=urls[0], meta={urls:urls, item:item, instructionset:v})
                inside crawl_chain:
                    results = crawl()
        """
        self.instructions = sort_od(OrderedDict(yaml.load(instructions)))
        #logging.log(logging.INFO, "\n{0}".format(simplejson.dumps(instructions_, indent=4, sort_keys=True)))

    @staticmethod
    def has_loop(k):
        return re.search(r'(\[([A-Za-z0-9]+\|)?([0-9\(\)]+)->([0-9\(\)]+)\])', 
                         k) is None

    @staticmethod
    def urls_from_loop(k, loop_expression):
        num_loop = re.search(
                r'(\[([A-Za-z0-9]+\s)?([0-9\(\)]+)->([0-9\(\)]+)\])', loop_expression)
        start = int(num_loop.groups()[2])
        end = int(num_loop.groups()[3])

        if num_loop.groups()[1]:
            #num_loop is of this format [getvar|a->b]; remove entire
            #bracketed expression and update getvar in url
            get_var = num_loop.groups()[1].replace("|", "")
            new_url = re.sub(
                r'(\[([A-Za-z0-9]+\s)?([0-9\(\)]+)->([0-9\(\)]+)\])',
                    "", k)
            #reset get variable to new value
            return [update_params(new_url, {get_var:i}) for i in range(start, 
                                                                       end+1)]
        else:
            #num_loop is of this format [a->b]; replace bracketed expression
            #with numbers
            return [re.sub(r'(\[([A-Za-z0-9]+\s)?([0-9\(\)]+)->([0-9\(\)]+)\])',
                                    "%s"%i, k) for i in range(start, end+1)]

    @staticmethod
    def urls_from_instructions(k, sel):
        """
        quick explanation of this regex monster:
        url->(.*?)(?:(\[([A-Za-z0-9]+\s)?([0-9\(\)]+)->([0-9\(\)]+)\])|$)

        a url can look like any of the following
        url->div/span/a/@href
        url->div/span/a/@href[a->b]
        url->div/span/a/@href[var|a->b]

        this regex matches capturing group 0 as the xpath expression itself,
        with a lazy matchall: (.*?)
        then it either matches brackets with anything in them, or the end 
        of the string

        this: (\[([A-Za-z0-9]+\|)?([0-9\(\)]+)->([0-9\(\)]+)\]) is used for 
        matching the number loop bracket notation for urls.
        it optionally matches an open bracket, some text, and whitespace,
        and then matches a number, an arrow, and a number.

        #group 0: xpath expression for urls
        #group 1: bracket expression. e.g. [1->2]
        #group 2: GET variable name. e.g. pageNumber|
        #group 3: start. e.g. 6
        #group 4: end. e.g. 9

        this function parses a url instruction, collects urls from a selector
        with the xpath from the instuction, applies number loop options and
        returns a list of urls
        """
        instruction = re.search('url->(.*?)(?:(\[([A-Za-z0-9]+\s)?([0-9\(\)]+)->([0-9\(\)]+)\])|$)', k)
        urls = []

        for url in sel.xpath(instruction.groups(0)).extract():
            if has_loop(url):
                urls.extend(urls_from_loop(url, 
                            instruction.groups(1)))
            else:
                urls.append(url)

        return urls 

    def parse(self, response):
        """use the parse function to crawl the instruction tree until we reach
        items:, then scrape recursively by continously yielding to crawl()
        until the entire instruction set has been followed
        """
        sel = Selector(response)
        items = []
        
        #...we've reached the items key in the instruction tree


        

    # def crawl_

    # # def process_loop(self, response):
    # #     sel = Selector(response)







    """
    smartphones:
        http://www.amazon.com/Best-Sellers-Electronics-Unlocked-Cell-Phones/zgbs/electronics/2407749011/ref=acs_ux_rw_ts_e_2407749011_more?pf_rd_p=2109755402&pf_rd_s=merchandised-search-5&pf_rd_t=101&pf_rd_i=2407749011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=176ZJ9DYYWYSZ2MW35GQ#[1->5]:
            items: 
                //div[@class="zg_itemImmersion"]:
                    img1: div[@class="zg_itemWrapper"]/div[@class="zg_image"]/div[@class="zg_itemImageImmersion"]/a//img/@src
                    div[@class="zg_itemWrapper"]/div[@class="zg_title"]/a/@href:
                        name: //span[contains(@id, "Title")]/text()
                        img2: //img[@id="landingImage"]/@src
                        features: //div[contains(@id, "feature-bullets")]//ul/li/span/text()       
                    reviews:
                        div[@class="zg_itemWrapper"]/div[@class="zg_reviews"]/span/a/@href[pageNumber|1->1]:
                            reviewId*: //div[@class="a-section review"]/@id
                            reviewTitle: //div[@class="a-section review"]/div[2]/a[2]/text()
                            reviewText: //div[@class="a-section review"]/div[5]/span/text()
                            reviewStars: //div[@class="a-section review"]/div[2]/a[1]/i/span/text()
        datasources:
            - reviews: amazon_highlights
    """
