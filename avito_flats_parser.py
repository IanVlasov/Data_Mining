from bs4 import BeautifulSoup
import requests
import time
import pymongo
from random import randint
import re


class FlatsParser:
    def __init__(self):
        self.USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 " \
                          "(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 "
        self.avito_base_url = 'https://www.avito.ru'
        self.flats_db = []

    def search_flats(self):
        next_url = '/sankt-peterburg/kvartiry'
        while next_url:
            avito_response = requests.get(f'{self.avito_base_url}{next_url}',
                                          headers={'User-Agent': self.USER_AGENT})
            if avito_response.status_code == 200:
                soup = BeautifulSoup(avito_response.text, 'lxml')
                flats_on_page = soup.find_all('a', attrs={'class': "item-description-title-link"})
                flats_links_on_page = []

                for flat in flats_on_page:
                    link = flat.attrs['href']
                    flats_links_on_page.append(link)

                for link in flats_links_on_page:
                    flat_response = requests.get(f'{self.avito_base_url}{link}',
                                                 headers={'User-Agent': self.USER_AGENT})
                    flat_soup = BeautifulSoup(flat_response.text, 'lxml')
                    self.flats_db.append(self.get_flat_record(flat_soup, link))
                    time.sleep(randint(1, 3))

                try:
                    next_url = soup.find('a', attrs={'class': 'pagination-page js-pagination-next'}).attrs['href']
                    params = {}
                except AttributeError:
                    break

                print('Идем дальше')

            else:
                print('Нас забанили!')
                break

    def get_flat_record(self, flat, link_):
        try:
            seller = flat.find('a', {'title': 'Нажмите, чтобы перейти в профиль'}).text.replace(u'\n', u'').\
                replace(' ', '')
            seller_link = flat.find('a', {'title': 'Нажмите, чтобы перейти в профиль'}).attrs['href']
        except AttributeError:
            seller = flat.find('a', {'title': 'Нажмите, чтобы перейти в магазин'}).text.replace(u'\n', u'').\
                replace(' ', '')
            seller_link = flat.find('a', {'title': 'Нажмите, чтобы перейти в магазин'}).attrs['href']
        price = int(flat.find('span', attrs={'class': 'js-item-price'}).attrs['content'])
        link = f"{self.avito_base_url}{link_}"
        parameters = flat.find_all('span', attrs={'class': 'item-params-label'})
        parameter_dict = {}

        for parameter in parameters:
            parameter_list = parameter.parent.text.split(':')
            parameter_dict[parameter_list[0]] = parameter_list[1]

        flat_record = {'Seller': seller,
                       'Seller_link': seller_link,
                       'Price': price,
                       'Link': link,
                       'Parameters': parameter_dict}
        return flat_record


if __name__ == '__main__':
    test = FlatsParser()
    test.search_flats()

    mongo_url = 'mongodb://localhost:27017'
    client = pymongo.MongoClient('localhost', 27017)
    database = client.avito
    collection = database.flats

    for flat_ in test.flats_db:
        collection.insert_one(flat_)
