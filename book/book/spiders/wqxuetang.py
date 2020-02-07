# -*- coding: utf-8 -*-
import scrapy
import json
from ..utils import WQXueTang
from ..items import BookItem

class WqxuetangSpider(scrapy.Spider):
    name = 'wqxuetang'
    allowed_domains = ['wqxuetang.com']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'book.middlewares.WQXUETANGBookDownloaderMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'book.pipelines.WQXUETANGBookImagePipeline': 300,
            'book.pipelines.WQXUETANGBookPDFPipeline': 600
        },
        'FILES_STORE': 'wqxuetang/'
    }

    def start_requests(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'lib-nuanxin.wqxuetang.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        }
        url = 'https://lib-nuanxin.wqxuetang.com/v1/search/inithomedata'
        # total = 4300
        total = 10
        size = 10
        max_page = int(total / size) + 1

        for i in range(1, max_page):
            yield scrapy.Request(url='{}?size={}&pn={}'.format(url, size, i), headers=headers, cookies=WQXueTang.get_cookies(), callback=self.parse)

    def parse(self, response):
        url = 'https://lib-nuanxin.wqxuetang.com/v1/read/initread'
        data = json.loads(response.text)
        bs = data['data']['list']
        meta = response.meta
        for b in bs:
            meta['id'] = b['numid']
            meta['author'] = b['author']
            meta['pubdate'] = b['pubdate']
            yield response.follow(url='{}?bid={}'.format(url, b['numid']), meta=meta, cookies=WQXueTang.get_cookies(), callback=self.parse_initread)

    def parse_initread(self, response):
        url = 'https://lib-nuanxin.wqxuetang.com/v1/read/catatree'
        data = json.loads(response.text)
        o = data['data']
        meta = response.meta
        meta['img'] = o['coverurl']
        meta['price'] = o['price']
        meta['name'] = o['name']
        meta['file_urls'] = [ 'https://lib-nuanxin.wqxuetang.com/page/img/{}/{}'.format(response.meta['id'], i) for i in range(1, int(o['pages']))]
        yield response.follow(url='{}?bid={}'.format(url, meta['id']), meta=meta, cookies=WQXueTang.get_cookies(), callback=self.parse_catatree)

    def parse_catatree(self, response):
        url = 'https://lib-nuanxin.wqxuetang.com/v1/read/k'
        data = json.loads(response.text)
        o = data['data']
        meta = response.meta
        meta['extra'] = o
        yield response.follow(url='{}?bid={}'.format(url, meta['id']), meta=meta, cookies=WQXueTang.get_cookies(), callback=self.parse_k)

    def parse_k(self, response):
        data = json.loads(response.text)
        o = data['data']
        meta = response.meta
        book = BookItem()
        book['img'] = meta['coverurl']
        book['price'] = meta['price']
        book['name'] = meta['name']
        book['publishdate'] = meta['pubdate']
        book['id'] = meta['id']
        book['writer'] = meta['author']
        book['file_urls'] = meta['file_urls']
        book['files'] = []
        book['key'] = o
        book['extra'] = meta['extra']
        yield book