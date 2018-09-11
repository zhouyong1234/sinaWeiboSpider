# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    collection = 'users'
    id = scrapy.Field()
    name = scrapy.Field()
    avatar = scrapy.Field()
    description = scrapy.Field()
    cover = scrapy.Field()
    weibo_url = scrapy.Field()
    verified = scrapy.Field()
    verified_type = scrapy.Field()
    verified_reason = scrapy.Field()
    fans_count = scrapy.Field()
    follows_count = scrapy.Field()
    crawled_at = scrapy.Field()


class UserRelationItem(scrapy.Item):
    collection = 'users'
    id = scrapy.Field()
    follows = scrapy.Field()
    fans = scrapy.Field()

class WeiboItem(scrapy.Item):
    collection = 'weibos'
    id = scrapy.Field()
    attitudes_count = scrapy.Field()
    comments_count = scrapy.Field()
    reposts_count = scrapy.Field()
    source = scrapy.Field()
    text = scrapy.Field()
    user = scrapy.Field()
    created_at = scrapy.Field()
    crawled_at = scrapy.Field()
