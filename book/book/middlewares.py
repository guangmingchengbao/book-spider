# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.retry import RetryMiddleware
import json
from scrapy import signals
from .utils import AESCipher, update_wqxuetang_cookies

class BookSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CMANUFBookDownloaderMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        headers = response.headers
        if 'Content-Type' in headers and headers['Content-Type'] == b'application/pdf':
            return response
        if 'Content-Type' in headers and headers['Content-Type'] == b'application/json':
            data = json.loads(response.text)
            if not data['success']:
                return self._retry(request, data['mess'], spider)
            return response
        return response


class Z51ZHYBookDownloaderMiddleware(RetryMiddleware):
    aes = AESCipher(b'luTDvdLNnJe9l30y')
    def process_response(self, request, response, spider):
        headers = response.headers
        if 'Content-Type' in headers and headers['Content-Type'] == b'application/pdf':
            author_key = self.aes.decrypt(request.meta['key'])
            aes = AESCipher(author_key.encode('utf-8'))
            return response.replace(body=aes.decrypt_body(response.body))
        if 'Content-Type' in headers and headers['Content-Type'] == b'application/json':
            data = json.loads(response.text)
            if not data['Success']:
                return self._retry(request, data['Description'], spider)
            return response
        if 'Content-Type' in headers and headers['Content-Type'] == b'text/html;charset=utf-8':
            return response
        return response


class WQXUETANGBookDownloaderMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        headers = response.headers
        if 'Content-Type' in headers and headers['Content-Type'] == b'image/jpeg':
            return response
        if 'Content-Type' in headers and headers['Content-Type'] == b'application/json':
            data = json.loads(response.text)
            if data['errcode'] == 3001:
                update_wqxuetang_cookies()
                return self._retry(request, data['errmsg'], spider)
            elif data['errcode'] != 0:
                return self._retry(request, data['errmsg'], spider)
            return response
        return response
