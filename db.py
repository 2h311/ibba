import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient


load_dotenv()
client = MongoClient(os.getenv("uri"))
db = client.get_database(os.getenv("databasename"))
