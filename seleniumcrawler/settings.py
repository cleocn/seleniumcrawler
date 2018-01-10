#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Scrapy settings for seleniumcrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'yaopin'

SPIDER_MODULES = ['seleniumcrawler.spiders']
NEWSPIDER_MODULE = 'seleniumcrawler.spiders'

SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.referer.RefererMiddleware': True,
}

ITEM_PIPELINES = {
    'seleniumcrawler.pipelines.SeleniumcrawlerPipeline': 300
}

COOKIES_ENABLED = True
COOKIES_DEBUG = True

LOG_LEVEL = 'INFO'
# LOG_FILE = 'scrapy.log'

# CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'
