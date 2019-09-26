from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.superjob import SuperjobSpider
from jobparser.spiders.avito import AvitoSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(AvitoSpider)
    # process.crawl(SuperjobSpider)
    # process.crawl(HhruSpider)
    process.start()
