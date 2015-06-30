import sys
import json
import requests
import time
import yaml
from collections import OrderedDict
from collections import defaultdict
from lxml import html



document = """
cars:
    http://www.autoevolution.com/cars/:
        //div[@class="brandlist"]/div/a/@href:
            modelname*: //div[@class="carslist-item"]/h2/a/@title
            //div[@class="carslist-item"]/h2/a/@href:
                //div[@class="seriesboxengines"]/ul/li[1]/a/@href:
                    cylinders: //dt[text()="Cylinders"]/following-sibling::dd[1]/text()
        brandname: //div[@class="brandlist"]/div/a/h2/text()
            """


def request_safely(url, throttle=0.0):
    r = requests.get(url)
    
    time.sleep(throttle/1000.0)

    sleeptime = 2
    conditions = [len(r.text) < 10]

    while any(conditions):
        print "request failed. trying again in %ss..." % sleeptime
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


yaml_doc = yaml.load(document2)
model_name, crawl_data = yaml_doc.iteritems().next()

doc = sort_od(OrderedDict(crawl_data))

result = crawl(doc)
print result