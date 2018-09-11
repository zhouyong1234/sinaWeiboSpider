# -*- coding: utf-8 -*-
import scrapy, json, re, time
from sinaWeibo.items import UserItem, UserRelationItem, WeiboItem

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['m.weibo.cn']
    user_url = 'https://m.weibo.cn/api/container/getIndex?containerid=100505{uid}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&since_id={page}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?containerid=230413{uid}_-_WEIBO_SECOND_PROFILE_WEIBO&page={page}'
    start_users = ['1669879400', '1223178222', '2970452952', '2334162530', '1291477752', '2706896955']

    def start_requests(self):
        for uid in self.start_users:
            yield scrapy.Request(url=self.user_url.format(uid=uid), callback=self.parse_user, dont_filter=False)

    def parse_user(self, response):
        """爬用户基本信息"""
        item = UserItem()
        results = json.loads(response.text)

        if results['data']['userInfo']:
            user_info = results['data']['userInfo']
            field_map = {
                'id': 'id',
                'name': 'screen_name',
                'avatar': 'avatar_hd',
                'cover': 'cover_image_phone',
                'weibo_url': 'profile_url',
                'verified': 'verified',
                'verified_type': 'verified_type',
                'verified_reason': 'verified_reason',
                'description': 'description',
                'fans_count': 'followers_count',
                'follows_count': 'follow_count',
            }
            for field, attr in field_map.items():
                item[field] = user_info.get(attr)
            print(item)
            yield item

            uid = user_info.get('id')
            # follows
            yield scrapy.Request(url=self.follow_url.format(uid=uid, page=1), callback=self.parse_follows, meta={'uid': uid, 'page': 1})
            # fans
            yield scrapy.Request(url=self.fan_url.format(uid=uid, page=1), callback=self.parse_fans, meta={'uid': uid, 'page': 1})
            # weibo
            yield scrapy.Request(url=self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibo, meta={'uid': uid, 'page': 1})

    def parse_follows(self, response):
        """爬关注列表"""
        results = json.loads(response.text)
        try:
            follows_info = results['data']['cards'][-1]['card_group']
            if follows_info:
                for follow_info in follows_info:
                    uid = follow_info['user']['id']
                    yield scrapy.Request(url=self.user_url.format(uid=uid), callback=self.parse_user)

                # follows_list
                uid = response.meta.get('uid')
                user_relation_item = UserRelationItem()
                follows = [{'id': follow['user']['id'], 'name': follow['user']['screen_name']} for follow in follows_info]
                user_relation_item['id'] = uid
                user_relation_item['follows'] = follows
                user_relation_item['fans'] = []
                yield user_relation_item

                # next page
                page = response.meta.get('page') + 1
                yield scrapy.Request(url=self.follow_url.format(uid=uid, page=page), callback=self.parse_follows, meta={'uid': uid, 'page': page})
        except:
            print('follows search nothing...')
            uid = response.meta.get('uid')
            user_relation_item = UserRelationItem()
            user_relation_item['id'] = uid
            user_relation_item['follows'] = []
            user_relation_item['fans'] = []


    def parse_fans(self, response):
        """爬粉丝列表"""
        results = json.loads(response.text)
        try:
            fans_info = results['data']['cards'][-1]['card_group']
            if fans_info:
                for fan_info in fans_info:
                    uid = fan_info['user']['id']
                    yield scrapy.Request(url=self.user_url.format(uid=uid), callback=self.parse_user)

                # fans_list
                user_relation_item = UserRelationItem()
                uid = response.meta.get('uid')
                fans = [{'id': fan['user']['id'], 'name':fan['user']['screen_name']} for fan in fans_info]
                user_relation_item['id'] = uid
                user_relation_item['follows'] = []
                user_relation_item['fans'] = fans
                yield user_relation_item

                # next page
                page = response.meta.get('page') + 1
                yield scrapy.Request(url=self.fan_url.format(uid=uid, page=page), callback=self.parse_fans, meta={'uid': uid, 'page': page})
        except:
            print('search notiong...')
            user_relation_item = UserRelationItem
            uid = response.meta.get('uid')
            user_relation_item['id'] = uid
            user_relation_item['follows'] = []
            user_relation_item['fans'] = []


    def parse_weibo(self, response):
        """爬微博文章"""
        weibo_item = WeiboItem()
        results = json.loads(response.text)
        weibos_info = results['data']['cards']
        if weibos_info:
            for weibo_info in weibos_info:
                if weibo_info['card_type'] == 9:
                    mblog = weibo_info['mblog']
                    field_map = {
                        'id': 'id',
                        'created_at': 'created_at',
                        'reposts_count': 'reposts_count',
                        'comments_count': 'comments_count',
                        'attitudes_count': 'attitudes_count',
                        'text': 'text',
                        'source': 'source',
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                        weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item

            # next page
            page = response.meta.get('page') + 1
            uid = response.meta.get('uid')
            yield scrapy.Request(url=self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibo, meta={'uid': uid, 'page': page})

    def parse_time(self, data):
        """时间标准化"""
        if re.match('刚刚', data):
            data = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        if re.match('\d+分钟前', data):
            minute = re.match('(\d+)', data).group(1)
            data = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前', data):
            hour = re.match('(\d+)', data).group(1)
            data = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*', data):
            data = re.match('昨天(.*)', data).group(1).strip()
            data = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60)) + ' ' + data
        if re.match('/d{2}-/d{2}', data):
            data = time.strftime('%Y+', time.localtime()) + data + '00:00'
        return data


