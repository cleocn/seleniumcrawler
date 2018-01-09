#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import mysql.connector
from seleniumcrawler.items import YaoPinItem,ShangPinItem
import logging 
import seleniumcrawler.config as CONFIG

class SeleniumcrawlerPipeline(object):

    def open_spider(self, spider):
        self.cnx = mysql.connector.connect(**CONFIG.MYSQL_CONN)
        self.cursor = self.cnx.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.cnx.close()
    
    def process_item(self, item, spider):
        if (not self.cnx or not self.cnx.is_connected()):
            self.cnx = mysql.connector.connect(**CONFIG.MYSQL_CONN)
            self.cursor = self.cnx.cursor()

        logging.info('process_item %s: (%s)'%(item['name'],type(item) ))

        #通用名 - 药品
        if isinstance(item, YaoPinItem):
            logging.debug('process_item 通用名药品')
            add_drug = ("INSERT INTO `通用名药品` "
                        " (`药品通用名`, `国产药品数`, `进口药品数`, `药品广告数`, page) "
                        " VALUES ( %(name)s, %(guochan_count)s, %(jinkou_count)s, %(guanggao_count)s , %(page)s ) "
                        " ON DUPLICATE KEY UPDATE `国产药品数`=%(guochan_count)s, `进口药品数`=%(jinkou_count)s, `药品广告数`=%(guanggao_count)s, page=%(page)s  ; "
                        )
            self.cursor.execute(add_drug, dict(item))
            return item
        #商品 ,
        if isinstance(item, ShangPinItem):
            logging.debug('process_item 商品')
            add_drug = ("INSERT INTO `商品` "
                        " (`table`, `sdaid`, `批文`, `生产单位`, `剂型`, `规格`, `药品`, url, page) "
                        " VALUES ( %(table)s, %(sdaid)s, %(piwen)s, %(shengchanqiye)s, %(jixing)s, %(guige)s , %(name)s , %(url)s, %(page)s ) "
                        " ON DUPLICATE KEY UPDATE `批文`=%(piwen)s, `生产单位`=%(shengchanqiye)s, `剂型`=%(jixing)s , `规格`=%(guige)s , `药品`=%(name)s ,url=%(url)s, page=%(page)s ; "
                        )
            self.cursor.execute(add_drug, dict(item))
            return item

        # self.cursor.close()
        # self.cnx.close()
        logging.error('process_item 错误类型')
        pass