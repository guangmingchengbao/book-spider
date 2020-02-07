# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import BookItem

# http://cdn.cmanuf.com/books/6/978-7-111-60487-7_1-1/Cover/978-7-111-60487-7_1-1_Cover1.jpg
# http://cdn.cmanuf.com/books/6/978-7-111-60487-7_1-1/PDF/978-7-111-60487-7_1-1_2.pdf
class CmanufSpider(scrapy.Spider):
    name = 'cmanuf'
    allowed_domains = ['cmanuf.com']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'book.middlewares.CMANUFBookDownloaderMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'book.pipelines.CMANUFBookPipeline': 300,
            'book.pipelines.CMANUFBookPDFPipeline': 600
        },
        'FILES_STORE': 'cmanuf/'
    }

    def start_requests(self):
        url = 'http://ebooks.cmanuf.com/getBookCategoryInfo'
        total = 18000
        size = 20
        max_page = int(total / size) + 1
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'ebooks.cmanuf.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        }
        for i in range(1, max_page):
            yield scrapy.Request(url='{}?page={}&limit={}'.format(url, i, size), headers=headers, callback=self.parse)

    def parse(self, response):
        data = json.loads(response.text)
        bs = data['module']
        for b in bs:
            book = BookItem()
            book['img'] = b['img']
            book['price'] = b['price']
            book['name'] = b['name']
            book['publishdate'] = b['publishdate']
            book['id'] = b['id']
            book['writer'] = b['writer']
            book['file_urls'] = []
            book['files'] = []
            yield book
