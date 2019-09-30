# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from jobparser.items import AvitoRealEstate


class AvitoRealEstateSpider(scrapy.Spider):
    name = 'avito_real_estate'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/rossiya/komnaty']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@class="pagination-page js-pagination-next"]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        ads_links = response.xpath('//a[@class="item-description-title-link"]/@href').extract()
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)
        pass

    @staticmethod
    def parse_ads(response: HtmlResponse):
        loader = ItemLoader(item=AvitoRealEstate(), response=response)
        loader.add_xpath('photos',
                         '//div[contains(@class, "gallery-img-wrapper")]//div[contains(@class, "gallery-img-frame")]/@data-url')
        loader.add_css('title', 'h1.title-info-title span.title-info-title-text::text')
        loader.add_xpath('params', '//li[@class="item-params-list-item"]/text()')
        loader.add_xpath('price', '//span[@class="price-value-string js-price-value-string"]//@content')
        yield loader.load_item()
