# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.http import HtmlResponse
from jobparser.items import SuperjobItem
from scrapy.loader import ItemLoader
from jobparser.items import get_sj_item


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bc%5D%5B0%5D=1']

    def parse(self, response):
        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        vacancies_on_page = response.css('div.f-test-vacancy-item a._2JivQ._3dPok::attr(href)').extract()

        for vacancy in vacancies_on_page:
            yield response.follow(vacancy, callback=self.vacancy_parse)

    @staticmethod
    def vacancy_parse(response: HtmlResponse):
        loader = ItemLoader(item=SuperjobItem(), response=response)
        response_script_tag = response.css('div._1Tjoc script').extract_first()
        response_param_str = response_script_tag[response_script_tag.index('>') + 1: response_script_tag.rindex('<')]
        response_param_dict = json.loads(response_param_str)

        yield get_sj_item(response_param_dict, loader)
        yield loader.load_item()
