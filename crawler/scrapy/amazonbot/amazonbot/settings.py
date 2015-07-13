# Scrapy settings for dirbot project

SPIDER_MODULES = ['amazonbot.spiders']
NEWSPIDER_MODULE = 'amazonbot.spiders'
DEFAULT_ITEM_CLASS = 'dirbot.items.AmazonItem'

#ITEM_PIPELINES = {'amazonbot.pipelines.FilterWordsPipeline': 1}
