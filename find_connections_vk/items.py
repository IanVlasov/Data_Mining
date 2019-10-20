# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


class FindConnectionsVkItem(scrapy.Item):
    _id = scrapy.Field()
    friends_chain = scrapy.Field()
