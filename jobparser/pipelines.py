# -*- coding: utf-8 -*-
from pymongo import MongoClient
from jobparser.database.base import VacancyDB
from jobparser.database.models import Vacancy
import scrapy
from scrapy.pipelines.images import ImagesPipeline


class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy
        # self.sql_db = VacancyDB('sqlite:///vacancy.sqlite')

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        # db_item = Vacancy(name=item.get('name'), spider=spider.name, url=item.get('url'), salary=item.get('salary'),
        #                   min_salary=item.get('min_salary'), max_salary=item.get('max_salary'),
        #                   employer=item.get('employer'), employer_url=item.get('employer_url'))
        # self.sql_db.add_salary(db_item)
        return item


class AvitoPhotosPipelines(ImagesPipeline):
    def get_media_requests(self, item, info):
        try:
            if item['photos']:
                for img in item['photos']:
                    try:
                        yield scrapy.Request(img)
                    except TypeError:
                        pass
        except KeyError:
            pass

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
