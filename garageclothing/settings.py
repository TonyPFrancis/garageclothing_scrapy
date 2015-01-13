# -*- coding: utf-8 -*-

# Scrapy settings for garageclothing project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import garageclothing

BOT_NAME = 'garageclothing'

SPIDER_MODULES = ['garageclothing.spiders']
NEWSPIDER_MODULE = 'garageclothing.spiders'

ITEM_PIPELINES = {
                'garageclothing.pipelines.GarageclothingPipeline' : 1,
}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'garageclothing (+http://www.yourdomain.com)'
