# -*- coding: utf-8 -*-
import scrapy
from ..utils import get_wqxuetang_cookies


class WqxuetangSpider(scrapy.Spider):
    name = 'wqxuetang'
    allowed_domains = ['wqxuetang.com']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'book.middlewares.WQXUETANGBookDownloaderMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'book.pipelines.WQXUETANGBookPDFPipeline': 300
        },
        'FILES_STORE': 'wqxuetang/'
    }

    def start_requests(self):
        headers = {
            'PHPSESSID': 'ge3sdklbkke33q4j3foqmpkbte',
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
            yield scrapy.Request(url='{}?size={}&pn={}'.format(url, size, i), headers=headers, cookies=get_wqxuetang_cookies(), callback=self.parse)

    def parse(self, response):
        url = 'https://lib-nuanxin.wqxuetang.com/v1/read/k'
        data = json.loads(response.text)
        bs = data['data']['list']
        for b in bs:
            meta = {
                'id': b['numid'],
                'author': b['author'],
                'pubdate': b['pubdate']
            }
            yield response.follow(url='{}?bid={}'.format(url, b['numid']), meta=meta, cookies=get_wqxuetang_cookies(), callback=self.parse_authorize)

    def parse_authorize(self, response):
        url = 'https://lib-nuanxin.wqxuetang.com/v1/read/initread'
        data = json.loads(response.text)
        o = data['data']
        meta = {
            'id': response.meta['id'],
            'author': response.meta['author'],
            'pubdate': response.meta['pubdate'],
            'key': o
        }
        yield response.follow(url='{}?bid={}'.format(url, response.meta['id']), meta=meta, cookies=get_wqxuetang_cookies(), callback=self.parse_detail)

    def parse_detail(self, response):
        data = json.loads(response.text)
        o = data['data']
        book = BookItem()
        book['img'] = o['coverurl']
        book['price'] = o['price']
        book['name'] = o['name']
        book['publishdate'] = response.meta['pubdate']
        book['id'] = response.meta['id']
        book['writer'] = response.meta['author']
        book['file_urls'] = [ 'https://lib-nuanxin.wqxuetang.com/page/img/{}/{}'.format(response.meta['id'], i) for i in o['pages']]
        book['files'] = []
        book['key'] = response.meta['key']
        yield book