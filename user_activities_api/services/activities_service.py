from datetime import datetime, timezone
from user_activities_api.db.mongo import user_activities_collection
from user_activities_api.utils.serializer import serialize_mongo


class ActivitiesService:

    @staticmethod
    async def add_favourite(user_id: str, movie_id: str):
        await user_activities_collection.update_one(
            {"user_id": user_id},
            {
                "$addToSet": {"favourite": movie_id},
                "$setOnInsert": {
                    "user_id": user_id,
                    "watchlist": []
                }
            },
            upsert=True
        )

    @staticmethod
    async def add_watchlist(user_id: str, movie_id: str):
        await user_activities_collection.update_one(
            {"user_id": user_id},
            {
                "$addToSet": {"watchlist": movie_id},
                "$setOnInsert": {
                    "user_id": user_id,
                    "favourite": []
                }
            },
            upsert=True
        )

    @staticmethod
    async def get_favourites(user_id: str):
        doc = await user_activities_collection.find_one({"user_id": user_id})
        return doc.get("favourite", []) if doc else []

    @staticmethod
    async def get_watchlist(user_id: str):
        doc = await user_activities_collection.find_one({"user_id": user_id})
        return doc.get("watchlist", []) if doc else []

    @staticmethod
    async def remove_favourite(user_id: str, movie_id: str):
        await user_activities_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"favourite": movie_id}}
        )

    @staticmethod
    async def remove_watchlist(user_id: str, movie_id: str):
        await user_activities_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"watchlist": movie_id}}
        )
