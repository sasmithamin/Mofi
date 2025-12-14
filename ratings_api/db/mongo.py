import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

if not MONGO_URI or not DB_NAME:
    raise Exception("MONGO_URI or MONGO_DB_NAME missing")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

ratings_collection = db["ratings"]
