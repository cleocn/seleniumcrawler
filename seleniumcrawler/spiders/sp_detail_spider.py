#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
from scrapy.item import Item, Field
from selenium import webdriver
import scrapy
from scrapy.http import FormRequest
import logging
from time import strftime
from datetime import timedelta
from datetime import datetime
import datetime
from scrapy.selector import HtmlXPathSelector
from seleniumcrawler.items import YaoPinItem,ShangPinItem
import re 
import numpy
import math
import seleniumcrawler.config as CONFIG
import mysql.connector

class SPDetailSpider(scrapy.spiders.Spider):
    name = "sp_detail"
    allowed_domains = ["sfda.gov.cn"]
    # start_urls = [
    #     "http://app2.sfda.gov.cn/datasearchp/gzcxSearch.do?page=1&searchcx=&optionType=V1&paramter0=null&paramter1=null&paramter2=null&formRender=cx"
    # ]
    cnx = False #还没有初始化
    
    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        # options.binary_location = '/usr/bin/google-chrome-unstable'
        options.add_argument('headless')
        options.add_argument('no-sandbox')
        # initialize the driver
        self.driver = webdriver.Chrome(chrome_options=options)
        # self.driver = webdriver.PhantomJS()#webdriver.Firefox()

        self.start_urls = self.getOne()

        # self.cursor.close()
        # self.cnx.close()
        logging.info(u"ShangPinSpider Init finished")
    
    def getOne(self):
        if (not self.cnx or not self.cnx.is_connected()):
            self.cnx = mysql.connector.connect(**CONFIG.MYSQL_CONN)
            self.cursor = self.cnx.cursor()
        sql = u"select * from `通用名药品` where loaded=0 limit 1"
        self.cursor.execute(sql)
        requests = []
        for item in self.cursor:
            # 国产药品 http://app2.sfda.gov.cn/datasearchp/all.do?page=2&name=%E5%B9%B2%E9%85%B5%E6%AF%8D%E7%89%87&tableName=TABLE25&formRender=gjcx&searchcx=&paramter0=&paramter1=&paramter2=
            # 进口药品 http://app2.sfda.gov.cn/datasearchp/all.do?page=2&name=%E4%BA%BA%E8%A1%80%E7%99%BD%E8%9B%8B%E7%99%BD&tableName=TABLE36&formRender=gjcx&searchcx=&paramter0=&paramter1=&paramter2=
            url_template = u"http://app2.sfda.gov.cn/datasearchp/all.do?page=%(page)s&name=%(drug)s&tableName=%(table)s&formRender=gjcx&"
            if int(item['guochan_count'])>0: # 国产药品
                page_count = int(math.ceil( int(item['guochan_count']) / 15.0 ))
                for pageno in numpy.arange(1,page_count+1,1):
                    url = url_template % {'table':'TABLE25', 'page':pageno, 'drug':item['name']}
                    requests.append(url) # {'url':url_gc, 'callback':self.parse_shangpin, 'meta':{'table':'TABLE25'} })
            if int(item['guochan_count'])>0: # 进口药品
                page_count = int( math.ceil( int(item['jinkou_count']) / 15.0 ))
                for pageno in numpy.arange(1,page_count+1,1):
                    url = url_template % {'table':'TABLE36', 'page':pageno, 'drug':item['name']}
                    requests.append(url) #{'url':url_gc, 'callback':self.parse_shangpin, 'meta':{'table':'TABLE36'} })
        return requests

    def parse(self, response):
        self.log(u'parse_shangpin_detail processing: %s'%response.url)
        
        self.driver.get(response.url)
        # wait up to 10 seconds for the elements to become available
        self.driver.implicitly_wait(10)
               
        items = []
        drug_items = self.driver.find_elements_by_xpath("//table[@class='msgtab']/tbody/tr[td]")

        self.log(u"found %d drug items." % drug_items.__len__())
        #each trip div has desribed two trip legs, we have to create 2 elements for each div
        for drug in drug_items:
            #1st trip leg
            item = ShangPinItem()
            item['name'] = (drug.find_elements_by_xpath("./td"))[1].text.encode("utf-8")#.decode("unicode-escape")
            item['url'] = (drug.find_elements_by_xpath("./td")[1]).find_elements_by_xpath("a").xpath('@href').extract()
            item['piwen'] = (drug.find_elements_by_xpath("./td"))[2].text.encode("utf-8")
            item['shengchanqiye'] = (drug.find_elements_by_xpath("./td"))[3].text.encode("utf-8")
            item['jixing'] = (drug.find_elements_by_xpath("./td"))[4].text.encode("utf-8")
            item['guige'] = (drug.find_elements_by_xpath("./td"))[5].text.encode("utf-8")

            yield item
            # items.append(item)
        # self.driver.close()
        # return items