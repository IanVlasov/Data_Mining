# -*- coding: utf-8 -*-
import scrapy
import json
import copy
from scrapy.http import Request
from scrapy.loader import ItemLoader
from find_connections_vk.items import FindConnectionsVkItem
from scrapy.exceptions import CloseSpider


class VkConnectionsSpider(scrapy.Spider):
    name = 'vk_connections'
    allowed_domains = ['vk.com']
    start_urls = ['https://vk.com']
    api_url = 'https://api.vk.com/method/'

    def __init__(self, uid_1, uid_2, user_login, token, *args, **kwargs):
        self.uid_1 = int(uid_1)
        self.uid_2 = int(uid_2)
        self.user_login = user_login
        self.access_token = token
        self.friends_chain = [self.uid_1, self.uid_2]
        super().__init__(*args, *kwargs)

    def start_requests(self):
        params = {'user_id': self.uid_1}
        yield Request(url=self.make_vk_api_url('friends.get', params), callback=self.first_check_if_friends)
        yield Request(url=self.make_vk_api_url('friends.get', params), callback=self.parse_list_of_friends,
                      meta={'curr_friends_chain': self.friends_chain},
                      dont_filter=True)

    def first_check_if_friends(self, response):
        friends_list = json.loads(response.body).get('response').get('items')

        if self.uid_2 in friends_list:
            loader = self.fill_item(self.friends_chain)
            yield loader.load_item()

        else:
            params = {'source_uid': self.uid_1, 'target_uids': self.uid_2}
            yield Request(url=self.make_vk_api_url('friends.getMutual', params),
                          callback=self.parse,
                          meta={'friends_list': [self.uid_1],
                                'curr_friends_chain': self.friends_chain,
                                'first_request': True})

    def parse(self, response):
        friends_chain = response.meta['curr_friends_chain']
        response_json = json.loads(response.body).get('response')
        mutual_friends = [friend for friend in response_json if friend.get('common_friends')]

        if mutual_friends:
            friends_chain.insert(-1, mutual_friends)
            loader = self.fill_item(friends_chain)
            yield loader.load_item()
            raise CloseSpider('chain was found')

        elif response.meta['first_request']:
            pass

        else:
            for friend in response.meta['friends_list']:
                curr_friends_chain = copy.deepcopy(friends_chain)
                curr_friends_chain.insert(-1, friend)
                params = {'user_id': friend}
                yield Request(self.make_vk_api_url('friends.get', params),
                              callback=self.parse_list_of_friends,
                              meta={'curr_friends_chain': curr_friends_chain})

    def parse_list_of_friends(self, response):
        list_of_friends = json.loads(response.body).get('response').get('items')

        if len(list_of_friends) > 500:
            split_list = self.split(list_of_friends, 500)

        else:
            split_list = [list_of_friends]

        for list_ in split_list:
            params = {'user_ids': ','.join(map(str, list_))}
            yield Request(self.make_vk_api_url('users.get', params),
                          callback=self.clear_list_of_friends,
                          errback=self.split_users_more,
                          meta={'curr_friends_chain': response.meta['curr_friends_chain'],
                                'list_of_friends': list_})

    def clear_list_of_friends(self, response):
        """Чистит лист друзей от закрытых и забаненных профилей, иначе friends.getMutual выдает
        ошибку при наличии хотя бы одного такого профиля."""
        dirty_curr_list = json.loads(response.body).get('response')

        if len(dirty_curr_list) > 100:
            split_list = self.split(dirty_curr_list, 100)
        else:
            split_list = [dirty_curr_list]

        for list_ in split_list:
            clear_curr_list = [itm.get('id') for itm in list_
                               if not itm.get('is_closed') and not itm.get('deactivated')]

            params = {'source_uid': self.uid_2, 'target_uids': ','.join(map(str, clear_curr_list))}
            yield Request(self.make_vk_api_url('friends.getMutual', params),
                          callback=self.parse,
                          meta={'friends_list': clear_curr_list,
                                'curr_friends_chain': response.meta['curr_friends_chain'],
                                'first_request': False})

    def split_users_more(self, failure):
        """Иногда проскакивают 414 ошибки из-за слишком длинного url в запросе,
        поэтому сокращаем количество юзеров в запросе users.get"""
        split_list = self.split(failure.request.meta['list_of_friends'],
                                len(failure.request.meta['list_of_friends']) // 2)

        for list_ in split_list:
            params = {'user_ids': ','.join(map(str, list_))}
            yield Request(self.make_vk_api_url('users.get', params),
                          callback=self.clear_list_of_friends,
                          errback=self.split_users_more,
                          meta={'curr_friends_chain': failure.request.meta['curr_friends_chain'],
                                'list_of_friends': list_})

    def make_vk_api_url(self, method, params):
        """Возвращает `url` для `api` запроса"""
        params_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        result = f'{self.api_url}{method}?{params_string}&access_token={self.access_token}&v=5.89'
        return result

    @staticmethod
    def fill_item(friends_chain):
        loader = ItemLoader(item=FindConnectionsVkItem())
        loader.add_value('friends_chain', friends_chain)
        return loader

    @staticmethod
    def split(arr, size):
        result_arr = []
        while len(arr) > size:
            pice = arr[:size]
            result_arr.append(pice)
            arr = arr[size:]
        result_arr.append(arr)
        return result_arr


