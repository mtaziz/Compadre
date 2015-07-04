#!/usr/bin/env python
"""Smart web scraper. Use this to define scraping instructions to automatically populate data models."""
import os
import sys
import re
import time
import requests
import simplejson
import yaml
from collections import OrderedDict
from collections import defaultdict
from lxml import html
from urlparse import urljoin

def request_safely(url, throttle=0.0, timeout_=5.0, timeout_read=5.0, sleeptime=2.0):
    r = None
    timeout = False
    errors = (lambda req: any([len(req.text) < 10,
                            req.status_code in [400, 403, 404, 405, 429, 500],
                            timeout]))

    try:
        "sleep, the send request"
        time.sleep(throttle/1000.0)
        r = requests.get(url=url,
                         timeout=(timeout_, timeout_read))
        if not errors(r):
            return r
    except requests.exceptions.ConnectTimeout as e:
        timeout = True

    while errors(r):
        print "request failed: %s. trying again in %ss..." % (r.status_code, sleeptime)
        time.sleep(sleeptime)
        sleeptime = min(60, sleeptime*2)

        "try request again"

    return r

def sort_od(od):
    """sort the resulting dictionary so that we evaluate the urls last. 
    New urls have nested attributes that are dependent on new pages, so we need
    to finish gathering all of the data associated with a current page before 
    moving onto a new one.
    """
    res = OrderedDict()
    for k, v in sorted(od.items(), key=lambda x: (1 if isinstance(x[1], dict) else 0)):
        if isinstance(v, dict):
            res[k] = sort_od(v)
        else:
            res[k] = v
    return res

def crawl(d, url=None, base="", desc={}, results=[], options=[]):

    if url:
        r = request_safely(url, 100)
        curr_page = html.fromstring(r.text)

        if "-v" in options:
            print "scraping: %s\n" % url

    temp_data = {}

    for k, v in d.iteritems():

        "if v is a dict, then k is a url"
        if isinstance(v, dict):

            if any(flag in k for flag in ['www.', 'http://']):
                "This is a normal url, continue the crawl"

                "check for url number loop instructions"
                num_loop = re.search(r'\[([0-9\(\)]+)->([0-9\(\)]+)\]', k)
                if num_loop:
                    for i in range(int(num_loop.group(1)), int(num_loop.group(2))+1):
                        "replace loop with actual number, build new url and crawl"
                        new_url = re.sub(r'(\[[0-9\(\)]+->[0-9\(\)]+\])', "%s"%i, k)
                        results.extend(crawl(v, new_url, base=urljoin(base, new_url), desc=desc, options=options))
                else:
                    results.extend(crawl(v, k, base=urljoin(base, url), desc=desc, options=options))

            else:
                """This is an xpath expression for a url. if the next entry in the instruction set is a url
                loop through xpath results (or 1 url), and make a new description to pass
                on to the next crawl() call
                """
                for index, url in enumerate( curr_page.xpath(k) ):
                    new_desc = {ke:ve[index] for ke,ve in temp_data.iteritems()}
                    new_desc.update(desc)

                    "if relative url, need to prepend base url"
                    url = urljoin(base, url)

                    """carry newly scraped data to the next crawl
                    """
                    results.extend(crawl(v, url, base=urljoin(base, url), desc=new_desc, options=options))

        else:
            "not a url, must be a field"
            temp_data[k] = curr_page.xpath(v)

    "check if we've reached the end of the tree"
    if not any(isinstance(v, dict) for k,v in d.iteritems()):
        tk,tv = temp_data.iteritems().next()

        result_data = []

        for index in range(len(tv)):
            new_desc = {ke:ve[index] for ke,ve in temp_data.iteritems()}
            new_desc.update(desc)

            if "-v" in options:
                print "scraped data: %s" % new_desc

            result_data.append(new_desc)

        return result_data

    return results

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "specify a yaml file to read crawl instructions from"
    
    elif os.path.exists(sys.argv[1]):

        file_ = open(sys.argv[1], 'r')
        yaml_ = yaml.load(file_.read())
        file_.close()

        print "crawl started...\nrun with -v for verbose crawling"

        model_name, crawl_data = yaml_.iteritems().next()
        result = crawl(sort_od(crawl_data), options=sys.argv[2:])

        final_result = []

        "combine duplicates"
        unique_field = [k for k in result[0].keys() if "*" in k][0]

        for r in result:

            dupe = [final_result.index(f) for f in final_result if r[unique_field] == f[unique_field]]

            if dupe:
                dupe = dupe[0]
                for k,v in r.iteritems():
                    if not v == final_result[dupe][k]:
                        if isinstance(final_result[dupe][k], list):
                            final_result[dupe][k].append(v)
                        else:
                            final_result[dupe][k] = [final_result[dupe][k], v]
            else:
                final_result.append(r)
            

        json_ = open("%s.json"%model_name, 'w')
        json_.write(simplejson.dumps(final_result, indent=4, sort_keys=True))
        json_.close()
        print "crawl result saved to %s.json" % model_name

    else:
        print "crawl instruction set not found. please fix your arguments and try again"