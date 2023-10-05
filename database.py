from pymongo import MongoClient, ASCENDING
from bson import ObjectId

DBClient = MongoClient("mongodb://localhost:27017/")

DBName = 'blogs'
Collection = 'blog'
UserCollection = 'user'
