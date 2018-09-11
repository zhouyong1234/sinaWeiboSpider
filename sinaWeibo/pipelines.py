# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sinaWeibo.items import WeiboItem, UserItem, UserRelationItem
from sinaWeibo.spiders.weibo import WeiboSpider
import time, pymongo

class WeiboPipeline(WeiboSpider):
    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            if item['created_at']:
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(data=item['created_at'])
        return item

class ItemPipeline(WeiboSpider):
    def process_item(self, item, spider):
        if isinstance(item, UserItem) or isinstance(item, WeiboItem):
            now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
            item['crawled_at'] = now
        return item

class MongoPipeline():
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongo_uri=crawler.settings['MONGO_URI'], mongo_db=crawler.settings['MONGO_DB'])

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # 以“id”创建索引，便于数据更新
        self.db[UserItem.collection].create_index([('id', pymongo.ASCENDING)])
        self.db[WeiboItem.collection].create_index([('id', pymongo.ASCENDING)])

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, UserItem) or isinstance(item, WeiboItem):
            # update(1.查询条件 {}， 2.item {}， 3.数据不存在时是否插入 True|False)
            # 若数据存在则数据更新，不存在则插入，添加 $set 操作符防止已存在的字段被清空
            self.db[item.collection].update({'id': item['id']}, {'$set': item}, True)
        if isinstance(item, UserRelationItem):
            self.db[item.collection].update(
                {'id': item['id']},
                {
                    # 向列表里插入数据
                    '$addToSet':
                        {
                            # $each 操作符遍历item列表，并逐条插入
                            'follows': {'$each': item['follows']},
                            'fans': {'$each': item['fans']},
                        }
                },
                True
            )