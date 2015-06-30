import os
import sys
import simplejson
import requests
import time
import yaml
from collections import OrderedDict
from collections import defaultdict
from lxml import html

def request_safely(url, throttle=0.0):
    r = requests.get(url)
    
    time.sleep(throttle/1000.0)

    sleeptime = 2
    conditions = [len(r.text) < 10]

    while any(conditions):
        print "a request failed. trying again in %ss..." % sleeptime
        time.sleep(sleeptime)
        sleeptime = min(60, sleeptime*2)

        r = requests.get(url)

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


def crawl(d, url=None, desc={}, results=[]):

    if url:
        r = request_safely(url, 200)
        curr_page = html.fromstring(r.text)

    temp_data = {}

    for k, v in d.iteritems():

        "if v is a dict, then k is a url"
        if isinstance(v, dict):

            if any(flag in k for flag in ['www.', 'http://']):
                "This is a normal url, continue the crawl"
                results.extend(crawl(v, k, desc))

            else:
                """This is an xpath expression for a url. if the next entry in the instruction set is a url
                loop through xpath results (or 1 url), and make a new description to pass
                on to the next crawl() call
                """
                for index, url in enumerate( curr_page.xpath(k) ):
                    new_desc = {ke:ve[index] for ke,ve in temp_data.iteritems()}
                    new_desc.update(desc)

                    """carry newly scraped fields to the next crawl
                    """
                    results.extend(crawl(v, url, new_desc))

        else:
            "not a url, must be a field"
            temp_data[k] = curr_page.xpath(v)

        "check if we've reached the end"
        if not any(isinstance(v, dict) for k,v in d.iteritems()):
            tk,tv = temp_data.iteritems().next()

            result_data = []

            for index in range(len(tv)):
                new_desc = {ke:ve[index] for ke,ve in temp_data.iteritems()}
                new_desc.update(desc)

                result_data.append(new_desc)

            return result_data

    return results

if __name__ == "__main__":
    
    if len(sys.argv) < 0:
        print "specify a yaml file to read crawl instructions from"
    
    elif os.path.exists(sys.argv[0]):

        file_ = open(sys.argv[0], 'r')
        yaml_ = yaml.load(file_.read())
        file_.close()

        model_name, crawl_data = yaml_doc.iteritems().next()
        result = crawl(doc)

        json_ = open("crawl_%s.json"%model_name, 'w')
        json_.write(simplejson.dumps(result, indent=4, sort_keys=True))
        json_.close()
        print "crawl result saved to crawl_%s.json" % model_name

    else:

        print "there was a problem. please fix your argument and try again"