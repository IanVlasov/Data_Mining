# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['https://www.avito.ru/rossiya/vakansii?q=python']
    main_url = 'https://www.avito.ru'

    def parse(self, response: HtmlResponse):
        vacancy_urls = response.xpath('//a[@class="item-description-title-link"]/@href').extract()
        next_page = response.xpath('//a[@class="pagination-page js-pagination-next"]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        for vacancy in vacancy_urls:
            yield response.follow(vacancy, callback=self.parse_vacancy)

    @staticmethod
    def parse_vacancy(response: HtmlResponse):
        name = \
            response.xpath('//div[@class="item-view-content"]//span[@class="title-info-title-text"]/text()').extract_first()

        url = response.url

        _tmp_cur = {'₽': 'RUB', '$': 'USD'}
        min_salary_str = \
            response.xpath(
                '//div[@class="item-view-content-right"]//span[@class="price-value-string js-price-value-string"]'
                '/span[@class="js-item-price"]/@content').extract_first()
        salary = {
            'currency': response.xpath('//div[@class="item-view-content-right"]//span[@itemprop="priceCurrency"]'
                                       '/@content').extract_first(),
            'min_value': int(min_salary_str) if min_salary_str else None
                  }

        employer = response.xpath('//div[@class="seller-info-name js-seller-info-name"]/a/text()').extract_first().strip()
        employer_url = response.xpath('//div[@class="seller-info-name js-seller-info-name"]/a/@href').extract_first()

        yield JobparserItem(name=name, url=url, salary=salary, employer=employer, employer_url=employer_url)
