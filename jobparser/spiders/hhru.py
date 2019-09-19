# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


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

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('div.vacancy-title h1.header::text').extract_first()
        url = response.url
        min_salary = response.css('div.vacancy-title meta[itemprop=minValue]::attr(content)').extract_first()
        max_salary = response.css('div.vacancy-title meta[itemprop=maxValue]::attr(content)').extract_first()
        employer = response.css('div.vacancy-company span[itemprop=name]::text').extract_first()
        employer_url = f'hh.ru' \
                       f'{response.css("div.vacancy-company a[itemprop=hiringOrganization]::attr(href)").extract_first()}'

        yield JobparserItem(name=name, url=url, min_salary=min_salary, max_salary=max_salary, employer=employer,
                            employer_url=employer_url)

