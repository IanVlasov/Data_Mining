# -*- coding: utf-8 -*-
from pymongo import MongoClient
from jobparser.database.base import VacancyDB
from jobparser.database.models import Vacancy


class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy
        self.sql_db = VacancyDB('sqlite:///vacancy.sqlite')

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        db_item = Vacancy(name=item.get('name'), spider=spider.name, url=item.get('url'), salary=item.get('salary'),
                          min_salary=item.get('min_salary'), max_salary=item.get('max_salary'),
                          employer=item.get('employer'), employer_url=item.get('employer_url'))
        self.sql_db.add_salary(db_item)
        return item
