# -*- coding: utf-8 -*-
import scrapy


class WqxuetangSpider(scrapy.Spider):
    name = 'wqxuetang'
    allowed_domains = ['wqxuetang.com']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'book.middlewares.WQXUETANGBookDownloaderMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'book.pipelines.WQXUETANGBookPipeline': 300,
            'book.pipelines.WQXUETANGBookPDFPipeline': 600
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
        url = 'https://lib-nuanxin.wqxuetang.com/v1/search/inithomedata?type=&size=10&pn=1'
        # total = 4300
        total = 10
        size = 10
        max_page = int(total / size) + 1

        for i in range(1, max_page):
            yield scrapy.Request(url='{}?size={}&pn={}'.format(url, size, i), headers=headers, callback=self.parse)

    def parse(self, response):
        data = json.loads(response.text)
        bs = data['data']['list']
        for b in bs:
            book = BookItem()
            book['img'] = b['coverurl']
            book['price'] = b['price']
            book['name'] = b['name']
            book['publishdate'] = b['pubdate']
            book['id'] = b['numid']
            book['writer'] = b['author']
            book['file_urls'] = ['']
            book['files'] = []
            yield book
