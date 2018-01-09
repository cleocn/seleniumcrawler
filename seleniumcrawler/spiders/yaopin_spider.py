#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
from scrapy.item import Item, Field
from selenium import webdriver
import scrapy
from scrapy.http import FormRequest
import logging
from scrapy.utils.log import configure_logging
from time import strftime
from datetime import timedelta
from datetime import datetime
import datetime
from scrapy.selector import HtmlXPathSelector
from seleniumcrawler.items import YaoPinItem,ShangPinItem
import re 
import numpy
import math

class YaoPinSpider(scrapy.spiders.Spider):
    name = "yaopin"
    allowed_domains = ["sfda.gov.cn"]
    start_urls = [
        "http://app2.sfda.gov.cn/datasearchp/gzcxSearch.do?page=1&searchcx=&optionType=V1&paramter0=null&paramter1=null&paramter2=null&formRender=cx"
    ]
    
    def __init__(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        # options.binary_location = '/usr/bin/google-chrome-unstable'
        options.add_argument('headless')
        # initialize the driver
        self.driver = webdriver.Chrome(chrome_options=options)
        # self.driver = webdriver.PhantomJS()#webdriver.Firefox()
        logging.info("YaoPinSpider Init finished")

    def parse(self, response):
        self.driver.get(response.url)
        logging.info('parse processing: %s'%response.url)
        # wait up to 10 seconds for the elements to become available
        self.driver.implicitly_wait(10)
               
        # /html/body/center/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[@width='200']
        pageNo_text =  self.driver.find_elements_by_xpath("//table/tbody/tr/td[@width='200' and @style='padding-left:30px']")[0].text
        # self.log("found pageNo_text %s ." % pageNo_text )
        pageNo = int(re.findall(r'/共(.*)页', pageNo_text.encode("utf-8"))[0])
        # self.log("found pageNo %d ." % pageNo )
        #each trip div has desribed two trip legs, we have to create 2 elements for each div
        for page in numpy.arange(1,pageNo+1):
            #1st trip leg
            url = "http://app2.sfda.gov.cn/datasearchp/gzcxSearch.do?page=%s&searchcx=&optionType=V1&paramter0=null&paramter1=null&paramter2=null&formRender=cx"%page
            
            yield scrapy.Request(url, callback=self.parse_drug, meta={'page':page})
        # self.driver.close()

    def parse_drug(self, response):
        self.driver.get(response.url)
        logging.info('parse_drug processing: %s'%response.url)
        # wait up to 10 seconds for the elements to become available
        self.driver.implicitly_wait(20)

        drug_items = self.driver.find_elements_by_xpath("//table[@width='943']/tbody/tr[@height='400']/td/table/tbody/tr[@height='30']")
        self.log("found %d drug items." % drug_items.__len__())
        #each trip div has desribed two trip legs, we have to create 2 elements for each div
        items = []
        for drug in drug_items:
            #1st trip leg
            item = YaoPinItem()
            item['name'] = (drug.find_elements_by_xpath("./td"))[0].text.encode("utf-8")#.decode("unicode-escape")
            logging.info('GET 通用名: %s .'%item['name'])
            item['guochan_count'] = (drug.find_elements_by_xpath("./td/table/tbody/tr/td/table/tbody/tr/td/font"))[0].text
            item['jinkou_count'] = (drug.find_elements_by_xpath("./td/table/tbody/tr/td/table/tbody/tr/td/font"))[1].text
            item['guanggao_count'] = (drug.find_elements_by_xpath("./td/table/tbody/tr/td/table/tbody/tr/td/font"))[2].text
            item['page'] = response.meta['page']

            # yield item
            items.append(item)
        
        return items
