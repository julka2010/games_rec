import re

import demjson
import scrapy
from scrapy.spiders import (
    CrawlSpider,
    Rule
)
from scrapy.linkextractors import LinkExtractor

class BGG_Games(CrawlSpider):
    name = 'bgg_games'
    allowed_domains = ['www.boardgamegeek.com']
    start_urls = ['https://www.boardgamegeek.com/browse/boardgame']

    rules = (
        Rule(
            LinkExtractor(allow=('/browse/boardgame', )),
            follow=True  #follow links to the next page
        ),
        Rule(
            LinkExtractor(allow=('/boardgame/')),
            callback='parse_game_page',
        )
    )

    def parse_game_page(self, response):
        game_id = int(re.search('\d+', response.request.url)[0])
        game_title_xpath = './/title/text()'
        game_info_xpath = './/script'
        search0 = r'GEEK.geekitemPreload = (?P<item>.*);.*GEEK.geekitemSettings'
        sel = scrapy.Selector(response)

        game_title = sel.xpath(game_title_xpath).extract_first()
        game_title = game_title.split('|')[0].strip()

        game_info = sel.xpath(game_info_xpath).extract_first()
        game_info = re.search(search0, game_info, flags=re.S)['item']
        game_info = demjson.decode(game_info)
        yield {
            'game_id': game_id,
            'title': game_title,
            'min_players': game_info['item']['minplayers'],
            'max_players': game_info['item']['maxplayers'],
            'min_playtime': game_info['item']['minplaytime'],
            'max_playtime': game_info['item']['maxplaytime'],
            'weight': game_info['item']['polls'
                ]['boardgameweight']['averageweight'],
            'dump': game_info,
        }
