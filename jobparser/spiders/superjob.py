# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


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

    def vacancy_parse(self, response: HtmlResponse):
        response_script_tag = response.css('div._1Tjoc script').extract_first()
        response_param_str = response_script_tag[response_script_tag.index('>') + 1: response_script_tag.rindex('<')]
        response_param_dict = json.loads(response_param_str)

        name = response_param_dict.get('title')
        url = response_param_dict.get('url')

        try:
            min_salary = response_param_dict.get('baseSalary').get('value').get('minValue')
        except AttributeError:
            min_salary = None

        try:
            max_salary = response_param_dict.get('baseSalary').get('value').get('maxValue')
        except AttributeError:
            max_salary = None

        try:
            employer = response_param_dict.get('hiringOrganization').get('name')
        except AttributeError:
            employer = None

        try:
            employer_url = response_param_dict.get('hiringOrganization').get('sameAs')
        except AttributeError:
            employer_url = None

        yield JobparserItem(name=name, url=url, min_salary=min_salary, max_salary=max_salary, employer=employer,
                            employer_url=employer_url)
