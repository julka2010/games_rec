import scrapy
from scrapy.spiders import (
    Spider
)
from scrapy.linkextractors import LinkExtractor

class BGG_Games(Spider):
    name = 'bgg_games'
    allowed_domains = ['www.boardgamegeek.com']
    search_url = 'https://www.boardgamegeek.com/xmlapi2/search?type=boardgame&exact=1&query='

    def start_requests(self):
        game_titles_file = self.games_list
        games = []
        with open(game_titles_file, 'r') as games_file:
            for row in games_file:
                games.append(row.strip().replace(' ', '+'))
        for game in games:
            yield scrapy.Request(url=self.search_url + game, callback=self.parse)

    def parse(self, response):
        game_id = response.xpath('//*[@id]/@id').extract_first()
        game_title = response.xpath('//name/@value').extract_first()
        return {'id': game_id, 'title': game_title}
