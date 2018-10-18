from pymongo import MongoClient


from lylwm_ui import settings



# Setup pymongo with port in helpers.py and the databases I'll use
client = MongoClient(settings.DB_HOST, settings.DB_PORT)
home_db = client[settings.DB]
home_db.authenticate(settings.DB_USER, settings.DB_PASS)

users = home_db.users
items = home_db.items
record = home_db.record