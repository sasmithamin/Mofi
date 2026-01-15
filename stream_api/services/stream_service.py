import uuid
from datetime import datetime
from stream_api.db.mongo import streams_collection
from stream_api.utils.serializer import serialize_mongo


class StreamService:

    @staticmethod
    async def create_stream(
        user_id: str,
        movie_id: str,
        title: str,
        description: str,
        date_time: str,
        is_live: bool = False
    ) -> dict:
        stream_id = str(uuid.uuid4())
        stream_key = str(uuid.uuid4())
        playback_id = str(uuid.uuid4())

        stream_doc = {
            "stream_id": stream_id,
            "user_id": user_id,
            "movie_id": movie_id,
            "title": title,
            "description": description,
            "date_time": date_time,   # human-readable
            "is_live": is_live,
            "stream_key": stream_key,
            "playback_id": playback_id,
            "created_at": datetime.utcnow()
        }

        await streams_collection.insert_one(stream_doc)
        return serialize_mongo(stream_doc)

    @staticmethod
    async def get_all_streams() -> list:
        streams = await streams_collection.find().to_list(100)
        return serialize_mongo(streams)

    @staticmethod
    async def delete_stream(stream_id: str) -> bool:
        result = await streams_collection.delete_one({"stream_id": stream_id})
        return result.deleted_count == 1
    
    @staticmethod
    async def start_stream(stream_key: str):
        stream = await streams_collection.find_one(
            {"stream_key": stream_key}
        )

        if not stream:
            return {
                "error": "Invalid stream key"
            }

        if stream.get("is_live") is True:
            return {
                "message": "Stream is already live",
                "is_live": True
            }

        await streams_collection.update_one(
            {"stream_key": stream_key},
            {
                "$set": {
                    "is_live": True,
                    "started_at": datetime.utcnow(),
                    "ended_at": None
                }
            }
        )

        return {
            "message": "Stream is now live",
            "is_live": True,
            "movie_id": stream["movie_id"]
        }

    @staticmethod
    async def stop_stream(stream_key: str):
        stream = await streams_collection.find_one(
            {"stream_key": stream_key}
        )

        if not stream:
            return {
                "error": "Invalid stream key"
            }

        if stream.get("is_live") is False:
            return {
                "message": "Stream is already stopped",
                "is_live": False
            }

        await streams_collection.update_one(
            {"stream_key": stream_key},
            {
                "$set": {
                    "is_live": False,
                    "ended_at": datetime.utcnow()
                }
            }
        )

        return {
            "message": "Stream stopped successfully",
            "is_live": False,
            "movie_id": stream["movie_id"]
        }

    @staticmethod
    async def get_stream_status(movie_id: str):
        stream = await streams_collection.find_one(
            {"movie_id": movie_id}
        )

        if not stream:
            return None

        return {
            "movie_id": movie_id,
            "is_live": stream.get("is_live", False),
            "started_at": stream.get("started_at"),
            "ended_at": stream.get("ended_at")
        }
    
    
