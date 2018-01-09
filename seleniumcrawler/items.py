# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YaoPinItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    guochan_count = scrapy.Field()
    jinkou_count = scrapy.Field()
    guanggao_count = scrapy.Field()
    page = scrapy.Field()


class ShangPinItem(scrapy.Item):
    # define the fields for your item here like:
    table = scrapy.Field()
    sdaid = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    piwen = scrapy.Field()
    shengchanqiye = scrapy.Field()
    jixing = scrapy.Field()
    guige = scrapy.Field()
    page = scrapy.Field()