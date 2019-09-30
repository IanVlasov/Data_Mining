# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import AvitoJobsItem
from scrapy.loader import ItemLoader


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
        loader = ItemLoader(item=AvitoJobsItem(), response=response)

        loader.add_xpath('name',
                         '//div[@class="item-view-content"]//span[@class="title-info-title-text"]/text()')

        loader.add_value('url', response.url)

        loader.add_xpath('salary',
                         '//span[@class="price-value-string js-price-value-string"]//@content')

        loader.add_xpath('employer',
                         '//div[@class="seller-info-name js-seller-info-name"]/a/text()')
        loader.add_xpath('employer_url',
                         '//div[@class="seller-info-name js-seller-info-name"]/a/@href')

        yield loader.load_item()
