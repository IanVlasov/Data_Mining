# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.loader import ItemLoader


def cleaner_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


def cleaner_hh_urls(url):
    return f'https://hh.ru{url[0][0]}'


def cleaner_avito_urls(url):
    return f'https://www.avito.ru{url[0]}'


def cleaner_params(list_of_params):
    list_of_params = [itm.strip() for itm in list_of_params if itm.strip()]
    dict_of_params = {
        'Square': list_of_params[0].strip().replace(u'\xa0', u''),
        'Total_rooms': int(list_of_params[1]) if list_of_params[1].isdigit()
        else list_of_params[1],
        'Floor': int(list_of_params[2]) if list_of_params[2].strip().isdigit()
        else list_of_params[2],
        'Total_floors': int(list_of_params[3]) if list_of_params[3].strip().isdigit()
        else list_of_params[3],
        'Type_of_house': list_of_params[4]
                      }
    return dict_of_params


def cleaner_salary_and_price_avito(list_to_change):
    dict_to_return = {
        'currency': list_to_change[1],
        'value': int(list_to_change[0]) if list_to_change[0].isdigit() else list_to_change[0],
              }
    return dict_to_return


def cleaner_salary_hh(salary):
    return int(salary[0]) if salary[0].isdigit() else salary[0]


def cleaner_avito_name(avito_name):
    name = avito_name[0].replace(u'\n', u'').strip()
    return name


def get_sj_item(response_param_dict, loader: ItemLoader):
    loader.add_value('name', response_param_dict.get('title'))
    loader.add_value('url', response_param_dict.get('url'))

    try:
        loader.add_value('min_salary', response_param_dict.get('baseSalary').get('value').get('minValue'))
    except AttributeError:
        loader.add_value('min_salary', None)

    try:
        loader.add_value('max_salary', response_param_dict.get('baseSalary').get('value').get('maxValue'))
    except AttributeError:
        loader.add_value('max_salary', None)

    try:
        loader.add_value('employer', response_param_dict.get('hiringOrganization').get('name'))
    except AttributeError:
        loader.add_value('employer', None)

    try:
        loader.add_value('employer_url', response_param_dict.get('hiringOrganization').get('sameAs'))
    except AttributeError:
        loader.add_value('employer_url', None)

    return loader


class AvitoRealEstate(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    params = scrapy.Field(output_processor=cleaner_params)
    price = scrapy.Field(output_processor=cleaner_salary_and_price_avito)


class AvitoJobsItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=cleaner_avito_name)
    url = scrapy.Field(output_processor=TakeFirst())
    salary = scrapy.Field(output_processor=cleaner_salary_and_price_avito)
    employer = scrapy.Field(output_processor=cleaner_avito_name)
    employer_url = scrapy.Field(output_processor=cleaner_avito_urls)


class SuperjobItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    min_salary = scrapy.Field(output_processor=TakeFirst())
    max_salary = scrapy.Field(output_processor=TakeFirst())
    employer = scrapy.Field(output_processor=TakeFirst())
    employer_url = scrapy.Field(output_processor=TakeFirst())


class HHItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    min_salary = scrapy.Field(output_processor=cleaner_salary_hh)
    max_salary = scrapy.Field(output_processor=cleaner_salary_hh)
    employer = scrapy.Field(output_processor=TakeFirst())
    employer_url = scrapy.Field(output_processor=cleaner_hh_urls)
