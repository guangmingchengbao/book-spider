# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    img = scrapy.Field() # : "https://cmpebooks.s3.cn-north-1.amazonaws.com.cn/books/0/978-7-111-04512-2_2-3/Cover/978-7-111-04512-2_2-3_Cover1.jpg"
    price = scrapy.Field() # : 206
    name = scrapy.Field() # : "机械工程手册：通用设备卷"
    publishdate = scrapy.Field() # : "2018-12-31"
    id = scrapy.Field() # : 10019
    writer = scrapy.Field() # : "机械工程手册电机工程手册编辑委员会"
    file_urls = scrapy.Field()
    files = scrapy.Field()
    key = scrapy.Field()
