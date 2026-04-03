import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://mongo_admin:password@localhost:27017",
)

MONGODB_DB = os.getenv("MONGODB_DB", "books")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[MONGODB_DB]


async def get_books_collection():
    yield database["books"]