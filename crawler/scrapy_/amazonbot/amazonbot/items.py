from scrapy.item import Item, Field

class AmazonItem(Item):
    name = Field()
    smallimg = Field()
    largeimg = Field()
    features = Field()
    reviews = Field()

