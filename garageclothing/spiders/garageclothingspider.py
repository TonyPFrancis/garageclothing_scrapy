import scrapy
from scrapy.http import Request
from scrapy.shell import inspect_response
from garageclothing.items import GarageclothingItem
from slugify import slugify
from datetime import datetime

class GarageclothingSpider(scrapy.Spider):
    name = 'garageclothingspider'
    allowed_domains = ['garageclothing.com',
                       'dynamiteclothing.com']
    start_urls = ['http://www.garageclothing.com']
    base_url = "http://www.garageclothing.com/"
    country_dict = {
        'CA': 'CANADA',
        'US': 'UNITED STATES',
    }

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

        # fetching country
        country_code = response.xpath(
            "//li[@class=\"siteDisplay\"]/a/span[@class=\"siteDisplayLanguage\"]/text()").extract()[0]
        country_code = country_code.encode('ascii', 'ignore').split('-')[0]
        country = self.country_dict[country_code]
        item['country'] = country

        # fetching country_slug
        item['country_slug'] = slugify(country)

        # fetcing id
        item['id'] = response.url

        # fetching product_id
        item['product_id'] = (response.xpath("//h3[@class=\"prodStylePDP\"]/text()").extract()[0]).split()[1]

        # fetching price
        item['price'] = response.xpath("//h2/span[@class=\"withSale\"]/text()").extract()[0].split('$')[1]

        # fetching size
        item['size'] = response.xpath("//div[@id=\"productSizes\"]/span/text()").extract()

        # fetching product_name
        product_name = response.xpath("//h1[@class=\"prodName prodNamePDP\"]/text()").extract()[0]
        item['product_name'] = product_name

        # fetching product_title_slug
        item['product_title_slug'] = slugify(product_name)

        # fetching product_img
        product_img = response.xpath("//div[@id=\"prodImageChangeContainer\"]//div[@id=\"additionalViewsPDP\"]//img/@src").extract()
        # converting images to high resolution
        product_img = [x.replace('104x143', '810x916') for x in product_img]
        item['product_img'] = product_img

        # fetching shop_slug
        item['shop_slug'] = slugify('garage'+' '+country_code)

        # fetching source_text
        item['source_text'] = slugify('garage'+' '+country_code)

        # fetching product_brand
        item['product_brand'] = 'GARAGE'

        # fetching brand_slug
        item['brand_slug'] = slugify('GARAGE')

        # fetching crawl_date
        item['crawl_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # fetching availability
        availability = response.xpath("//div[@id=\"stockAvailabilityMsg\"]/text()").extract()[0].strip()
        if not availability:
            item['availability'] = False
        else:
            item['availability'] = availability
        
        yield item
        inspect_response(response)
