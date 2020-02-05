# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import BookItem


class Z51zhySpider(scrapy.Spider):
    name = 'z51zhy'
    allowed_domains = ['51zhy.cn']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'book.middlewares.Z51ZHYBookDownloaderMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            # 'book.pipelines.Z51ZHYBookPipeline': 300,
            'book.pipelines.Z51ZHYBookPDFPipeline': 600
        },
        'FILES_STORE': 'z51zhy/'
    }

    def start_requests(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'yd.51zhy.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        }
        url = 'http://yd.51zhy.cn/ebook/web/search/search4HomePage'
        total = 20600
        # total = 15
        size = 15
        max_page = int(total / size) + 1

        for i in range(1, max_page):
            yield scrapy.Request(url='{}?currentPage={}'.format(url, i), headers=headers, callback=self.parse)

    def parse(self, response):
        url = 'https://bridge.51zhy.cn/transfer/content/authorize'
        ids = response.css('ul li.ebook-item input.search_Input::attr(value)').getall()
        for id in ids:
            meta = {
                'id': id,
            }
            form = {
                'id': id,
                'BridgePlatformName': 'phei_yd_web',
                'DeviceToken': 'ebookE0415F559DF90E6D52123BBB653436B2'
            }
            yield scrapy.FormRequest(url=url, meta=meta, formdata=form, callback=self.parse_authorize)
    
    def parse_authorize(self, response):
        data = json.loads(response.text)
        o = data['Data']
        meta = {
            'id': response.meta['id'],
            'url': o['Url'],
            'key': o['Key']
        }
        url = 'https://bridge.51zhy.cn/transfer/Content/Detail?BridgePlatformName=phei_yd_web&id={}'.format(response.meta['id'])
        yield response.follow(url=url, meta=meta, callback=self.parse_detail)

    def parse_detail(self, response):
        data = json.loads(response.text)
        o = data['Data']
        book = BookItem()
        book['img'] = o['CoverUrl']
        book['price'] = o['CurrentPrice']
        book['name'] = o['Title']
        book['publishdate'] = o['PublishDate']
        book['id'] = response.meta['id']
        book['writer'] = o['Author']
        book['file_urls'] = [response.meta['url']]
        book['files'] = []
        book['key'] = response.meta['key']
        yield book

