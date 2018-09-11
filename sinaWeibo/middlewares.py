# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests, logging, json

class ProxyMiddleware(object):
    def __init__(self, proxy_url):
        self.logger = logging.getLogger(__name__)
        self.proxy_url = proxy_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(proxy_url=crawler.settings['PROXY_URL'])

    def get_random_proxy(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        if request.meta.get('retry_times'):
            proxy = self.get_random_proxy()
            if proxy:
                url = 'http://' + str(proxy)
                self.logger.debug('使用代理：' + str(proxy))
                request.meta['proxy'] = url

class CookiesMiddleware():
    def __init__(self, cookies_url):
        self.logger = logging.getLogger(__name__)
        self.cookies_url = cookies_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(cookies_url=crawler.settings.get('COOKIES_URL'))

    def get_random_cookies(self):
        try:
            response = requests.get(self.cookies_url)
            if response.status_code == 200:
                cookies = json.loads(response.text)
                return cookies
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        self.logger.debug('正在获取cookies')
        cookies = self.get_random_cookies()
        if cookies:
            requests.cookies = cookies
            self.logger.debug('使用cookies ' + json.dumps(cookies))


