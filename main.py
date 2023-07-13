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
            self.authors.append({
                "fullname": adapter["fullname"],
                "born_date": adapter["born_date"],
                "born_location": adapter["location_born"],
                "description": adapter["description"],
            })

        if 'quote' in adapter.keys():
            self.quotes.append({
                "tags": adapter["keywords"],
                "author": adapter["author"],
                "quote": adapter["quote"],
            })
        return

    def close_spider(self, spider):
        with open('json/qoutes.json', 'w', encoding='utf-8') as fq:
            json.dumps(self.quotes, fq, ensure_ascii=False)

        with open('json/authors.json', 'w', encoding='utf-8') as fa:
            json.dumps(self.authors, fa, ensure_ascii=False)


class AuthorsSpider(scrapy.Spider):
    name = 'authors'
    custom_settings = {'ITEM_PIPELINES': {Q_Pipline: 100}}
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='quote']"):
            keywords = quote.xpath("div[@class='tags']/a/text()").extract()
            author = quote.xpath("span/small/text()").get().strip()
            quote_text = quote.xpath("span[@class='text']/text()").get().strip()

            yield QuoteItem(keywords=keywords, author=author, quote_text=quote_text)
            yield response.follow(url=self.start_urls[0] + quote.xpath('span/a/@href').get(),
                                  callback=self.parse_author)

            next_link = response.xpath("//li[@class='next']/a/@href").get()
            if next_link:
                yield scrapy.Request(url=self.start_urls[0] + next_link)

    def parse_author(self, response):
        author = response.xpath("/html//div[@class='author-details']")
        fullname = author.xpath("h3[@class='author-title']/text()").get().strip()
        date_born = author.xpath("p/span[@class='author-born-date']/text()").get().strip()
        location_born = author.xpath("p/span[@class='author-born-location']/text()").get().strip()
        bio = author.xpath("div[@class='author-description']/text()").get().strip()

        yield AuthorItem(fullname=fullname, date_born=date_born, location_born=location_born, description=bio)


def load_json():
    with open('json/authors.json', 'r', encoding='utf-8') as fh:
        result = json.load(fh)

        for i in result:
            new_author = Authors()
            new_author.description = i['description']
            new_author.born_date = datetime.strptime(i['born_date'], '%B %d, %Y').date()
            new_author.born_location = i['born_location']
            new_author.fullname = i['fullname']
            new_author.save()

    with open('json/quotes.json', 'r', encoding='utf-8') as fh:
        result = json.load(fh)

        for i in result:
            authors = Authors.objects(fullname=i['author'])

            if len(authors) > 0:
                cur_author = [0]

            new_quote = Quotes(author=cur_author)
            new_quote.quote = i['quote']
            new_quote.tags = i['tags']
            new_quote.save()


if __name__ == '__main__':
   process = CrawlerProcess()
   process.crawl(AuthorsSpider)
   process.start()

   load_json()

