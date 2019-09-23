# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy.http import HtmlResponse
from urllib.parse import urlencode, urljoin
from copy import deepcopy
from instagram_parser.items import InstagramParserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    variables_base = {'fetch_mutual': 'false', "include_reel": 'true'}
    followers = {}

    def __init__(self, user_links, login, pswrd, *args, **kwargs):
        self.user_links = user_links
        self.login = login
        self.pswrd = pswrd
        self.query_hash_posts = '58b6785bea111c67129decbe6a448951'
        self.query_hash_likes = 'd5d763b1e2acf209d62d22d184488e57'
        self.query_hash_comments = '97b41c52301f77ce508f55e66d17620e'
        self.query_hash_threaded_comments = '51fdd02b67508306ad4484ff574a0b62'
        super().__init__(*args, *kwargs)

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            'https://www.instagram.com/accounts/login/ajax/',
            method='POST',
            callback=self.parse_users,
            formdata={'username': self.login, 'password': self.pswrd},
            headers={'X-CSRFToken': csrf_token}
        )

    def parse_users(self, response: HtmlResponse):
        j_body = json.loads(response.body)
        if j_body.get('authenticated'):
            for user in self.user_links:
                yield response.follow(urljoin(self.start_urls[0], user),
                                      callback=self.parse_user,
                                      cb_kwargs={'user': user})

    def parse_user(self, response: HtmlResponse, user):
        user_id = self.fetch_user_id(response.text, user)
        user_vars = deepcopy(self.variables_base)
        user_vars.update({'id': user_id, 'first': 10})
        yield response.follow(self.make_graphql_url(user_vars, self.query_hash_posts),
                              callback=self.parse_posts,
                              cb_kwargs={'user_vars': user_vars, 'user': user, 'user_id': user_id})

    def parse_posts(self, response: HtmlResponse, user_vars, user, user_id):
        data = json.loads(response.body)
        first_posts = data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')

        user_vars.pop('id')

        for post in first_posts:
            post_id = post.get('node').get('id')
            shortcode = post.get('node').get('shortcode')
            post_url = urljoin(self.start_urls[0], 'p/' + shortcode)
            image = post.get('node').get('display_url')
            text = post.get('node').get('edge_media_to_caption').get('edges')[0].get('node').get('text')

            item = InstagramParserItem(post_id=post_id, owner=user, owner_id=user_id, shortcode=shortcode, post_url=post_url,
                                       image=image, text=text, commented_by=[], liked_by=[])

            comment_vars = {'shortcode': shortcode, 'first': 100}
            like_vars = {'shortcode': shortcode, 'include_reel': 'true', 'first': 100}

            yield response.follow(self.make_graphql_url(comment_vars, self.query_hash_comments),
                                  callback=self.parse_comments,
                                  cb_kwargs={'item': item, 'comment_vars': comment_vars})

            yield response.follow(self.make_graphql_url(like_vars, self.query_hash_likes),
                                  callback=self.parse_likes,
                                  cb_kwargs={'item': item, 'like_vars': like_vars})

            yield item

    def parse_comments(self, response: HtmlResponse, comment_vars, item: InstagramParserItem):
        data = json.loads(response.body)

        comments = data.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get('edges')

        for comment in comments:
            item.get('commented_by').append(comment.get('node').get('owner'))

            if comment.get('node').get('edge_threaded_comments').get('count'):
                threaded_comments = comment.get('node').get('edge_threaded_comments').get('edges')
                for threaded_comment in threaded_comments:
                    item.get('commented_by').append(threaded_comment.get('node').get('owner'))

                if comment.get('node').get('edge_threaded_comments').get('page_info').get('has_next_page'):
                    comment_id = comment.get('node').get('id')
                    threaded_vars = comment_vars
                    threaded_vars.pop('shortcode')
                    threaded_vars.update({
                        'comment_id': comment_id,
                        'first': 10,
                        'after': comment.get('node').get('edge_threaded_comments').get('page_info').get('end_cursor')
                    })

                    yield response.follow(self.make_graphql_url(threaded_vars, self.query_hash_threaded_comments),
                                          callback=self.parse_threaded_comments,
                                          cb_kwargs={'item': item, 'threaded_vars': threaded_vars})

        if data.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get('page_info').get('has_next_page'):
            comment_vars.update({
                'after': data.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get('page_info').get('end_cursor')})

            yield response.follow(self.make_graphql_url(comment_vars, self.query_hash_comments),
                                  callback=self.parse_comments,
                                  cb_kwargs={'item': item, 'user_vars': comment_vars})

        yield item


    def parse_threaded_comments(self, response: HtmlResponse, threaded_vars, item: InstagramParserItem):
        data = json.loads(response.body)

        threaded_comments = data.get('data').get('comment').get('edge_threaded_comments').get('edges')

        for comment in threaded_comments:
            item.get('commented_by').append(comment.get('node').get('owner'))

        if data.get('data').get('comment').get('edge_threaded_comments').get('page_info').get('has_next_page'):
            threaded_vars.update({
                'after': data.get('data').get('comment').get('edge_threaded_comments').get('page_info').get('end_cursor')
            })

            yield response.follow(self.make_graphql_url(threaded_vars, self.query_hash_threaded_comments),
                                  callback=self.parse_threaded_comments,
                                  cb_kwargs={'item': item, 'threaded_vars': threaded_vars})

        yield item

    def parse_likes(self, response: HtmlResponse, like_vars, item: InstagramParserItem):
        data = json.loads(response.body)

        likes = data.get('data').get('shortcode_media').get('edge_liked_by').get('edges')

        for like in likes:
            item.get('liked_by').append(like.get('node').get('reel').get('owner'))

        if data.get('data').get('shortcode_media').get('edge_liked_by').get('page_info').get('has_next_page'):
            like_vars.update({
                'after': data.get('data').get('shortcode_media').get('edge_liked_by').get('page_info').get('end_cursor')
            })

            yield response.follow(self.make_graphql_url(like_vars, self.query_hash_likes),
                                  callback=self.parse_likes,
                                  cb_kwargs={'item': item, 'like_vars': like_vars})

        yield item



    @staticmethod
    def fetch_csrf_token(text):
        """Используя регулярные выражения парсит переданную строку на наличие
        `csrf_token` и возвращет его."""
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    @staticmethod
    def fetch_user_id(text, username):
        """Используя регулярные выражения парсит переданную строку на наличие
        `id` нужного пользователя и возвращет его."""
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def make_graphql_url(self, user_vars, target_hash):
        """Возвращает `url` для `graphql` запроса"""
        result = '{url}query_hash={hash}&{variables}'.format(
            url=self.graphql_url, hash=target_hash,
            variables=urlencode(user_vars)
        )
        return result

