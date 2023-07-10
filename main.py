import argparse
import json

from _datetime import datetime
from models import Authors, Quotes

parser = argparse.ArgumentParser(description='load or find')
parser.add_argument('-a', '--action')


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
                cur_author = authors[0]

            new_quote = Quotes(author=cur_author)
            new_quote.quote = i['quote']
            new_quote.tags = i['tags']
            new_quote.save()


def find_in_db():
    while True:
        command = input('enter command >>>')
        if command[:4] == 'exit':
            break

        else:
            arg = command.split(':')
            f_name = arg[0]

            if f_name == 'name':
                authors = Authors.objects(fullname=arg[1])
                [print(author.to_mongo().to_dict()) for author in authors]

            if f_name == 'tag':
                quotes = Quotes.objects(tags=arg[1])
                [print(quote.to_mongo().to_dict()) for quote in quotes]

            if f_name == 'tags':
                quotes = Quotes.objects(tags__in=arg[1].split(' '))
                [print(quote.to_mongo().to_dict()) for quote in quotes]


if __name__ == '__main__':
    if 'load' == vars(parser.parse_args()).get('action'):
        load_json()
    find_in_db()
