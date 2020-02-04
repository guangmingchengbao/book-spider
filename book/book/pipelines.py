# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
import scrapy
import re


class CMANUFBookPipeline(object):
    # replace: https://cmpebooks.s3.cn-north-1.amazonaws.com.cn/books/0/978-7-111-04504-1_2-3/PDF/978-7-111-04504-1_2-3_2.pdf
    # valid: https://cmpebooks.s3.cn-north-1.amazonaws.com.cn/books/0/978-7-111-04504-1_2-3/Cover/978-7-111-04504-1_2-3_Cover1.jpg
    # invalid: http://images.hzmedia.com.cn/11120366/yuantu/20191018144018072.jpg
    def process_item(self, item, spider):
        if re.match(r'^(.+)\/Cover\/(.+)_Cover[0-9].jpg$', item['img']) is not None:
            item['file_urls'] = [re.sub(r'^(.+)\/Cover\/(.+)_Cover[0-9].jpg$', r'\1/PDF/\2_2.pdf', item['img'])]
            item['files'] = []
            return item
        else:
            raise DropItem('Missing pdf {} {}'.format(item['id'], item['name']))


class CMANUFBookPDFPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        headers = {
            'User-Agent': 'PostmanRuntime/7.22.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Host': 'cmpebooks.s3.cn-north-1.amazonaws.com.cn',
            'Connection': 'keep-alive',
            'Referer': 'https://cmpebooks.s3.cn-north-1.amazonaws.com.cn/pdfReader/generic/build/pdf.worker.js'
        }
        for file_url in item['file_urls']:
            yield scrapy.Request(file_url, headers=headers)


class Z51ZHYBookPipeline(object):
    def process_item(self, item, spider):
        if re.match(r'^(.+)\/Cover\/(.+)_Cover[0-9].jpg$', item['img']) is not None:
            item['file_urls'] = [re.sub(r'^(.+)\/Cover\/(.+)_Cover[0-9].jpg$', r'\1/PDF/\2_2.pdf', item['img'])]
            item['files'] = []
            return item
        else:
            raise DropItem('Missing pdf {} {}'.format(item['id'], item['name']))


class Z51ZHYBookPDFPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Host': 'yypt-sw.oss-cn-beijing.aliyuncs.com',
            'Connection': 'keep-alive',
        }
        meta = {
            'key': item['key']
        }
        for file_url in item['file_urls']:
            yield scrapy.Request(file_url, meta=meta, headers=headers)


class WQXUETANGBookPipeline(object):
    def process_item(self, item, spider):
        if re.match(r'^(.+)\/Cover\/(.+)_Cover[0-9].jpg$', item['img']) is not None:
            item['file_urls'] = [re.sub(r'^(.+)\/Cover\/(.+)_Cover[0-9].jpg$', r'\1/PDF/\2_2.pdf', item['img'])]
            item['files'] = []
            return item
        else:
            raise DropItem('Missing pdf {} {}'.format(item['id'], item['name']))


class WQXUETANGBookPDFPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        headers = {
            'User-Agent': 'PostmanRuntime/7.22.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Host': 'cmpebooks.s3.cn-north-1.amazonaws.com.cn',
            'Connection': 'keep-alive',
            'Referer': 'https://cmpebooks.s3.cn-north-1.amazonaws.com.cn/pdfReader/generic/build/pdf.worker.js'
        }
        for file_url in item['file_urls']:
            yield scrapy.Request(file_url, headers=headers)