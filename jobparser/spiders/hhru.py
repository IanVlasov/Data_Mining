# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from jobparser.items import HHItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://spb.hh.ru/search/vacancy?area=113&st=searchVacancy&text=Python']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        vacancies_on_page = response.css('div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header '
                                         'a.bloko-link::attr(href)').extract()

        for vacancy in vacancies_on_page:
            yield response.follow(vacancy, callback=self.vacancy_parse)

    @staticmethod
    def vacancy_parse(response: HtmlResponse):
        loader = ItemLoader(item=HHItem(), response=response)
        loader.add_css('name', 'div.vacancy-title h1.header::text')
        loader.add_value('url', response.url)
        loader.add_css('min_salary', 'div.vacancy-title meta[itemprop=minValue]::attr(content)')
        loader.add_css('max_salary', 'div.vacancy-title meta[itemprop=maxValue]::attr(content)')
        loader.add_css('employer', 'div.vacancy-company span[itemprop=name]::text')
        loader.add_css('employer_url', "div.vacancy-company a[itemprop=hiringOrganization]::attr(href)")

        yield loader.load_item()

