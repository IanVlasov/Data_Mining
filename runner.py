import os
from os.path import join, dirname
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from find_connections_vk import settings
from find_connections_vk.spiders.vk_connections import VkConnectionsSpider

do_env = join(dirname(__file__), '.env')
load_dotenv(do_env)

USER_ID = os.getenv('USER_ID')
TOKEN = os.getenv('TOKEN')

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(VkConnectionsSpider, '19587588', '20367747', USER_ID, TOKEN)
    process.start()
