import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")


client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

movies_collection = db["movies"]
pre_ratings_collection = db["pre_ratings"]
post_ratings_collection = db["post_ratings"]
