import os
from os.path import join, dirname
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram_parser import settings
from instagram_parser.spiders import instagram
from instagram_parser.spiders.instagram import InstagramSpider

do_env = join(dirname(__file__), '.env')
load_dotenv(do_env)

IM_LOGIN = os.getenv('IM_LOGIN')
IM_PWD = os.getenv('IM_PWD')

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider, ['strugatskaya'], IM_LOGIN, IM_PWD)
    process.start()