import json
import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from itemadapter import ItemAdapter
from _datetime import datetime

from connect import connect
from models import Authors, Quotes


class QuoteItem(Item):
    keywords = Field()
    author = Field()
    quote = Field()


class AuthorItem(Item):
    fullname = Field()
    date_born = Field()
    location_born = Field()
    description = Field()


class Q_Pipline:
    quotes = []
    authors = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if 'fullname' in adapter.keys():
            Q_Pipline.authors.append({
                "fullname": adapter["fullname"],
                "date_born": adapter["date_born"],
                "location_born": adapter["location_born"],
                "description": adapter["description"],
            })

        if 'quote' in adapter.keys():
            Q_Pipline.quotes.append({
                "tags": adapter["keywords"],
                "author": adapter["author"],
                "quote": adapter["quote"],
            })
        return

    def close_spider(self, spider):
        with open('json/quotes.json', 'w', encoding='utf-8') as fq:
            json.dump(Q_Pipline.quotes, fq, ensure_ascii=False, indent=4)

        with open('json/authors.json', 'w', encoding='utf-8') as fa:
            json.dump(Q_Pipline.authors, fa, ensure_ascii=False, indent=4)


class MainSpider(scrapy.Spider):
    name = 'main_spider'
    custom_settings = {'ITEM_PIPELINES': {Q_Pipline: 100}}
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response, *args):
        for item in response.xpath("/html//div[@class='quote']"):
            keywords = [e.strip() for e in item.xpath("div[@class='tags']/a[@class='tag']/text()").extract()]
            author = item.xpath("span/small[@class='author']/text()").get().strip()
            quote = item.xpath("span[@class='text']/text()").get().strip()

            yield QuoteItem(keywords=keywords, author=author, quote=quote)
            yield response.follow(url=self.start_urls[0] + item.xpath('span/a/@href').get(),
                                  callback=self.parse_author)

            next_link = response.xpath("//li[@class='next']/a/@href").get()
            if next_link:
                yield scrapy.Request(url=self.start_urls[0] + next_link)

    def parse_author(self, response, *args):
        author = response.xpath("/html//div[@class='author-details']")
        fullname = author.xpath("h3[@class='author-title']/text()").get().strip()
        date_born = author.xpath("p/span[@class='author-born-date']/text()").get().strip()
        location_born = author.xpath("p/span[@class='author-born-location']/text()").get().strip()
        bio = author.xpath("div[@class='author-description']/text()").get().strip()

        yield AuthorItem(fullname=fullname, date_born=date_born, location_born=location_born, description=bio)


if __name__ == '__main__':
   process = CrawlerProcess()
   process.crawl(MainSpider)
   process.start()


