from mongoengine import connect
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

user = config.get('DEV_DB', 'user')
password = config.get('DEV_DB', 'password')
db_name = config.get('DEV_DB', 'db_name')
domain = config.get('DEV_DB', 'domain')

connect(host=f"""mongodb+srv://{user}:{password}@{domain}/{db_name}?retryWrites=true&w=majority""", ssl=True)
