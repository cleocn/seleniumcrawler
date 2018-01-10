#!/usr/bin/python
# -*- coding: UTF-8 -*-

from scrapy.item import Item, Field
from selenium import webdriver
import scrapy
from scrapy.http import FormRequest
import logging
from seleniumcrawler.items import HospitalItem
import re 
import numpy
import math
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class hospitalSpider(scrapy.spiders.Spider):
    name = "hosp"
    allowed_domains = ["hqms.org.cn"]
    start_urls = [
        "https://www.hqms.org.cn/usp/roster/index.jsp"
    ]
    
    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        # options.binary_location = '/usr/bin/google-chrome-unstable'
        # options.binary_location = '/usr/bin/google-chrome-stable'
        options.add_argument('headless')
        options.add_argument('no-sandbox')
        # initialize the driver
        self.driver = webdriver.Chrome(chrome_options=options)
        # self.driver = webdriver.PhantomJS()#webdriver.Firefox()
        logging.info("hospitalSpider Init finished")

    def parse(self, response):
        self.driver.get(response.url)
        logging.info('parse processing: %s'%response.url)
        # wait up to 10 seconds for the elements to become available
        self.driver.implicitly_wait(10)
               
        # 省列表
        provinceList =  self.driver.find_elements_by_xpath("//select[@class='province_select']/option[@value!='']")
        logging.info('provinceList count: %s 个 。'%len(provinceList))
        for province in provinceList:
            #
            prov = {
                'provinceId': province.get_attribute('value'),
                'provinceName': province.text
            }
            url = "https://www.hqms.org.cn/usp/roster/rosterInfo.jsp?provinceId=%s&htype=&hgrade=&hclass=&hname=&_=1515493618508"%prov['provinceId']
            
            yield scrapy.Request(url, callback=self.parse_2, meta=prov)
        # self.driver.close()

    def parse_2(self, response):
        self.driver.get(response.url)
        logging.info('parse_drug processing: %s'%response.url)
        # wait up to 10 seconds for the elements to become available
        self.driver.implicitly_wait(20)
        
        hospital_json = json.loads(response.body)

        self.log("found %d 医院 items." % hospital_json.__len__())
        #each trip div has desribed two trip legs, we have to create 2 elements for each div
        items = []
        for hospital in hospital_json:
            #1st trip leg
            item = HospitalItem(hospital)
            item['provinceName'] = response.meta['provinceName']
            item['name'] = item['hName']
            # yield item
            items.append(item)
        
        return items
