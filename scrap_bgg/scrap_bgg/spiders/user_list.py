import scrapy
from scrapy.spiders import (
    CrawlSpider,
    Rule
)
from scrapy.linkextractors import LinkExtractor

#Idea for next scrapping
#Url https://www.boardgamegeek.com/api/collections?ajax=1&objectid=<game_id>&objecttype=thing&oneperuser=1&pageid=1&rated=1&require_review=true&showcount=50&sort=review_tstamp
#ratings = json.loads(response)
#ratings['items'][<rating_id>]['rating']
#ratings['items'][<rating_id>]['user']['username']

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

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse_users_page(self, response):
        user_page_xpath = './/a[contains(@href, "/user/")]/@href'
        ratings_query = '?rated=1'
        users = response.xpath(user_page_xpath).extract()
        for user in users:
            yield response.follow(
                'https://www.boardgamegeek.com/collection' + user + ratings_query,
                callback=self.parse_users_ratings,
            )

    def parse_users_ratings(self, response):
        game_row_xpath = '//table[contains(@class, "collection_table")]/tr'
        game_url_xpath = './/a[contains(@href, "boardgame")]/@href'
        user_rating_xpath = './/div[contains(@class, "ratingtext")]/text()'

        sel = scrapy.Selector(response)
        games = sel.xpath(game_row_xpath)
        item = {}
        username = response.request.url.split('/')[-1].split('?')[0]
        for game in games[1:]:  #Ignore header row
            url = game.xpath(game_url_xpath)
            rating = game.xpath(user_rating_xpath)
            game_id = url.extract_first().split('/')[2]
            yield {'username': username, 'game_id': game_id, 'rating': rating.extract_first()}
