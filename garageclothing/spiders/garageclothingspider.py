from _mysql import result
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
    # dict to find the country wrt site info
    country_dict = {
        'CA': 'CANADA',
        'US': 'UNITED STATES',
    }
    total_product = 0
    skipped_product = 0
    # current runtime of spider
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def parse(self, response):
        redirect_url = response.xpath(
            "//meta/@content").extract()[0].split('URL=')[1]
        print ">>>>>>>>>>\nRedirecting to URL\n" + redirect_url
        yield Request(url=redirect_url, callback=self.parseredirect)

    def parseredirect(self, response):
        '''
        fuction to redirect to "http://www.garageclothing.com/ca/"
        :param response:
        :return:
        '''
        redirect_url = self.base_url + "ca/"
        print ">>>>>>>>>>\nRedirecting to URL\n" + redirect_url
        yield Request(url=redirect_url, callback=self.parsemainpage)


    def parsemainpage(self, response):
        '''
        function to fetch categoru urls
        :param response:
        :return:
        '''
        print ">>>>>>>>>> Current URL"
        print response.url

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
        '''
        function to parse category and get the product items
        :param response:
        :return:
        '''
        print ">>>>>>>>>> Category URL"
        print "URL : " + response.url
        next_url = response.xpath("//figure[@class=\"prodlistingFrag productListingElement \"]/@nextpage").extract()
        if next_url:
            next_url = next_url[0]
            print ">>>>>>>>>> NEXT URL"
            print next_url

        productURL = response.xpath(
            "//div[@class='prodListingImg']/a/@href").extract()
        if productURL:
            for product in productURL:
                print ">>>>>>>>>> Product URL"
                print self.base_url + product
                yield Request(url=self.base_url + product, callback=self.parse_product)


        if next_url:
            yield Request(url=self.base_url+next_url, callback=self.parse_category)


    def parse_product(self, response):
        '''
        function to parse product
        :param response:
        :return:
        '''
        print ">>>>>>>>>>"
        print "URL : " + response.url

        # create GarageclothingItem
        item = GarageclothingItem()

        # fetcing id
        item['id'] = response.url


        try:

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

            # fetching product_id
            item['product_id'] = (response.xpath("//h3[@class=\"prodStylePDP\"]/text()").extract()[0]).split()[1]

            # fetching price
            price_list = response.xpath("//h2[@class=\"prodPricePDP\"]//text()").extract()
            if len(price_list) > 1:
                price = response.xpath("//h2[@class=\"prodPricePDP\"]/span[@class=\"withSale\"]/text()").extract()[0]
            elif len(price_list) == 1:
                price = response.xpath("//h2[@class=\"prodPricePDP\"]/text()").extract()[0]
            price = price.replace('$','')
            item['price'] = float(price)

            # fetching size
            item['size'] = response.xpath("//div[@id=\"productSizes\"]/span/text()").extract()

            # fetching product_name
            product_name = response.xpath("//h1[@class=\"prodName prodNamePDP\"]/text()").extract()[0]
            item['product_name'] = product_name.strip()

            # fetching product_title_slug
            item['product_title_slug'] = slugify(product_name.strip())

            # fetching product_img
            product_img = response.xpath("//div[@id=\"prodImageChangeContainer\"]//div[@id=\"additionalViewsPDP\"]//img/@src").extract()
            # converting images to high resolution
            product_img = ["http:"+x.replace('104x143', '810x916') for x in product_img]
            item['product_img'] = product_img

            # fetching shop_slug
            item['shop_slug'] = slugify('garage'+'_'+country_code)

            # fetching source_text
            item['source_text'] = 'garage'+'_'+country_code

            # fetching product_brand
            item['product_brand'] = 'GARAGE'

            # fetching brand_slug
            item['brand_slug'] = slugify('GARAGE')

            # fetching crawl_date
            item['crawl_date'] = self.current_time

            # fetching availability
            availability = response.xpath("//div[@id=\"stockAvailabilityMsg\"]/text()").extract()[0].strip()
            if not availability:
                item['availability'] = False
            else:
                item['availability'] = True

            # fetching category_list
            category_list = response.xpath("//ul[@class=\"breadcrumbs\"]/li//text()").extract()

            # fetching main_category
            main_category = category_list[1]

            if main_category in ["what's new"]:
                # skipping if item is in "what's new" category
                print "*** SKIP"
                self.skipped_product += 1
                return
            else:
                # assign value if item is not in "what's new" category
                item['main_category'] = main_category

            # fetching category_slug
            item['category_slug'] = slugify(main_category)

            #fetching product_category
            item['product_category'] = category_list[2]

            # fetching subcategory_slug
            item['subcategory_slug'] = slugify(category_list[2])



            self.total_product += 1
            print "TOTAL PRODUCT = %s" % self.total_product
            print "SKIPPED PRODUCT = %s" % self.skipped_product
            # yielding item to pipeline
            yield item

        except Exception, e:
            print "***exception at"
            print item['id']



