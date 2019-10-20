# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class FindConnectionsVkPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vk_connections

    def process_item(self, item, spider):
        mongo_coll_name = f"{spider.name} for {item.get('friends_chain')[0]} and {item.get('friends_chain')[-1]}"
        collection = self.mongo_base[mongo_coll_name]
        collection.insert_one(item)
        return item
