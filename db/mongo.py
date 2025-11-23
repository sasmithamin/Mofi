from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Force load .env from project root
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

if not MONGO_URI:
    raise Exception("MONGO_URI is missing in .env file")

if not MONGO_DB_NAME:
    raise Exception("MONGO_DB_NAME is missing in .env file")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]

print("DB NAME:", MONGO_DB_NAME)