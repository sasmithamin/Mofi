from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

if not MONGO_URI or not MONGO_DB_NAME:
    raise Exception("Missing MongoDB env variables")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]

user_activities_collection = db["user_activities"]
