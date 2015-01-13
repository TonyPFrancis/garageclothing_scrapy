import scrapy
from scrapy.http import Request
from scrapy.shell import inspect_response
from garageclothing.items import GarageclothingItem


class GarageclothingSpider(scrapy.Spider):
    name = 'garageclothingspider'
    allowed_domains = ['garageclothing.com',
                       'dynamiteclothing.com']
    start_urls = ['http://www.garageclothing.com']
    base_url = "http://www.garageclothing.com/"

    def parse(self, response):
        redirect_url = response.xpath(
            "//meta/@content").extract()[0].split('URL=')[1]
        print ">>>>>>>>>>\nRedirecting to URL\n" + redirect_url
        yield Request(url=redirect_url, callback=self.parseredirect)

    def parseredirect(self, response):
        redirect_url = self.base_url + "ca/"
        print ">>>>>>>>>>\nRedirecting to URL\n" + redirect_url
        yield Request(url=redirect_url, callback=self.parsemainpage)

    def parsemainpage(self, response):
        print ">>>>>>>>>> Current URL"
        print response.url
        '''
        # fetching selectors os mainCategoryMenu
        mainCategoryMenu = response.xpath(
            "//div[@id='mainCategoryMenu']/ul/li/span/a[not(contains(@title, \"WHAT\'S NEW\") or contains(@title, \"SALE\") or contains(@title, \"Blog\"))]")
        '''
        # fetching URL of mainCategoryMenu items
        mainCategoryMenuURL = response.xpath(
            "//div[@id='mainCategoryMenu']/ul/li/span/a[not(contains(@title, \"WHAT\'S NEW\") or contains(@title, \"SALE\") or contains(@title, \"Blog\"))]/@href").extract()
        if mainCategoryMenuURL:
            for category in mainCategoryMenuURL:
                print ">>>>>>>>>>"
                request_url = self.base_url + category
                print "Fetchign items from " + request_url
                yield Request(url=request_url, callback=self.parse_category)

        else:
            print ">>>>>>>>>>"
            print "Couldn't find main category list"
            return

    def parse_category(self, response):
        print ">>>>>>>>>>"
        print "URL : " + response.url
        productURL = response.xpath(
            "//div[@class='prodListingImg']/a/@href").extract()
        if productURL:
            for product in productURL:
                yield Request(url=self.base_url + product, callback=self.parse_product)

    def parse_product(self, response):
        print ">>>>>>>>>>"
        print "URL : " + response.url
        # create GarageclothingItem
        item = GarageclothingItem()
        # fetching product_description
        product_description = response.xpath(
            "//div[@class=\"productDescriptionContent\"]//text()").extract()
        product_description = '. '.join(
            [x.strip() for x in product_description if x.strip()])
        item['product_description'] = product_description
        inspect_response(response)
