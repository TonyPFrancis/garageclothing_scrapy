# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GarageclothingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_description = scrapy.Field()
    country = scrapy.Field()
    country_slug = scrapy.Field()
    id = scrapy.Field()
    product_id = scrapy.Field()
    price = scrapy.Field()
    size = scrapy.Field()
    product_name = scrapy.Field()
    product_title_slug = scrapy.Field()
    product_img = scrapy.Field()
    shop_slug = scrapy.Field()
    source_text = scrapy.Field()
    product_brand = scrapy.Field()
    brand_slug = scrapy.Field()
    crawl_date = scrapy.Field()
    availability = scrapy.Field()
    main_category = scrapy.Field()
    category_slug = scrapy.Field()
    product_category = scrapy.Field()
    subcategory_slug = scrapy.Field()