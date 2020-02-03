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

    def parse(self, response):
        pass
