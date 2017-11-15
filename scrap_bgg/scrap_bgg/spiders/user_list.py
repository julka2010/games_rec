import scrapy
from scrapy.spiders import (
    CrawlSpider,
    Rule
)
from scrapy.linkextractors import LinkExtractor

class BGG_UserList(CrawlSpider):
    name = 'bgg_userlist'
    allowed_domains = ['www.boardgamegeek.com']
    start_urls = ['https://www.boardgamegeek.com/users']

    rules = (
        Rule(
            LinkExtractor(allow=('/users',), deny=('\?country',  )),
            callback='parse_users_page',
            follow=True  #follow links to the next page
        ),
    )

    def parse_users_page(self, response):
        username_xpath = './/a[contains(@href, "/user/")]/text()'
        item = {}
        item['username'] = response.xpath(username_xpath).extract_first()
        return item
