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
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class ShangPinSpider(scrapy.spiders.Spider):
    name = "shangpin"
    allowed_domains = ["sfda.gov.cn"]
    # start_urls = [
    #     "http://app2.sfda.gov.cn/datasearchp/gzcxSearch.do?page=1&searchcx=&optionType=V1&paramter0=null&paramter1=null&paramter2=null&formRender=cx"
    # ]
    cnx = False
    
    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        # options.binary_location = '/usr/bin/google-chrome-unstable'
        # options.binary_location = '/usr/bin/google-chrome-stable'
        options.add_argument('no-sandbox')
        options.add_argument('headless')
        # self.options = options
        # initialize the driver
        self.driver = webdriver.Chrome(chrome_options=options)
        # self.driver = webdriver.PhantomJS()#webdriver.Firefox()

        logging.info("ShangPinSpider Init finished")
    
    def closed(self, reason):
        logging.info("closed ++++++++++++++++++++++++++")
        self.driver.close()
        self.cursor_update.close()
        self.cursor.close()
        self.cnx.close()
        pass

    def start_requests(self):
        logging.info('start_requests++++++')
        if (not self.cnx or not self.cnx.is_connected()):
            self.cnx = mysql.connector.connect(**CONFIG.MYSQL_CONN)
            self.cursor = self.cnx.cursor(buffered=True)
            self.cursor_update = self.cnx.cursor()
        allLoaded = False
        No = 1
        while not allLoaded:
            sql = "select `药品通用名` as drug_name, `国产药品数` as guochan_count, `进口药品数` as jinkou_count from `通用名药品` where loaded=0 limit 5"
            self.cursor.execute(sql)
            allLoaded = self.cursor.rowcount==0
            requests = []

            for (drug_name, guochan_count, jinkou_count) in self.cursor:
                guochan_count = int(guochan_count)
                jinkou_count = int(jinkou_count)
                # 国产药品 http://app2.sfda.gov.cn/datasearchp/all.do?page=2&name=%E5%B9%B2%E9%85%B5%E6%AF%8D%E7%89%87&tableName=TABLE25&formRender=gjcx&searchcx=&paramter0=&paramter1=&paramter2=
                # 进口药品 http://app2.sfda.gov.cn/datasearchp/all.do?page=2&name=%E4%BA%BA%E8%A1%80%E7%99%BD%E8%9B%8B%E7%99%BD&tableName=TABLE36&formRender=gjcx&searchcx=&paramter0=&paramter1=&paramter2=
                url_template = "http://app2.sfda.gov.cn/datasearchp/all.do?page=%(page)s&name=%(drug)s&tableName=%(table)s&formRender=gjcx&"
                if guochan_count>0: # 国产药品
                    page_count = int(math.ceil( guochan_count / 15.0 ))
                    for pageno in numpy.arange(1,page_count+1,1):
                        pageno = str(pageno)
                        url = url_template % {'table':'TABLE25', 'page':pageno, 'drug': drug_name }
                        # requests.append(url) # {'url':url_gc, 'callback':self.parse_shangpin, 'meta':{'table':'TABLE25'} })
                        yield scrapy.Request(**{'url':url, 'callback':self.parse, 'meta':{'table':'TABLE25', 'page':pageno} })
                if jinkou_count>0: # 进口药品
                    page_count = int( math.ceil( jinkou_count / 15.0 ))
                    for pageno in numpy.arange(1,page_count+1,1):
                        pageno = str(pageno)
                        url = url_template % {'table':'TABLE36', 'page':pageno, 'drug': drug_name }
                        # requests.append(url) #{'url':url_gc, 'callback':self.parse_shangpin, 'meta':{'table':'TABLE36'} })
                        yield scrapy.Request(**{'url':url, 'callback':self.parse, 'meta':{'table':'TABLE36', 'page':pageno} })
            sql = "update `通用名药品` set loaded=1 where `药品通用名` = %(drug_name)s "
            self.cursor_update.execute(sql,{'drug_name':drug_name})
            logging.info('DRUG %s schedued. No：%s '%(drug_name, No) )
            No += 1
        # return requests

    def parse(self, response):
        self.log('parse_shangpin processing: %s'%response.url)
        
        self.driver.get(response.url)
        # wait up to 10 seconds for the elements to become available
        self.driver.implicitly_wait(20)
               
        items = []
        drug_items = self.driver.find_elements_by_xpath("//table[@class='msgtab']/tbody/tr[td]")

        logging.info("found %d 商品 items in %s."%(drug_items.__len__(), response.url) )
        #each trip div has desribed two trip legs, we have to create 2 elements for each div
        for drug in drug_items:
            #1st  
            item = ShangPinItem()
            item['url'] = (drug.find_elements_by_xpath("./td/a"))[0].get_attribute('href')
            item['table'] = response.meta['table']
            item['name'] = (drug.find_elements_by_xpath("./td"))[1].text.encode("utf-8")#.decode("unicode-escape")
            item['sdaid'] = item['url'].split("&Id=")[1]
            item['piwen'] = (drug.find_elements_by_xpath("./td"))[2].text.encode("utf-8")
            item['shengchanqiye'] = (drug.find_elements_by_xpath("./td"))[3].text.encode("utf-8")
            item['jixing'] = (drug.find_elements_by_xpath("./td"))[4].text.encode("utf-8")
            item['guige'] = (drug.find_elements_by_xpath("./td"))[5].text.encode("utf-8")
            item['page'] = response.meta['page']

            # yield item
            items.append(item)
        
        # driver.close()
        # self.driver.quit()
        return items
