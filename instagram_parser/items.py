# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramParserItem(scrapy.Item):
    _id = scrapy.Field()
    post_id = scrapy.Field()
    owner = scrapy.Field()
    owner_id = scrapy.Field()
    shortcode = scrapy.Field()
    post_url = scrapy.Field()
    image = scrapy.Field()
    text = scrapy.Field()
    liked_by = scrapy.Field()
    commented_by = scrapy.Field()
