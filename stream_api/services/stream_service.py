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
    async def validate_stream_key(stream_key: str):
        # Find stream by stream_key
        stream = await streams_collection.find_one(
            {"stream_key": stream_key}
        )

        if not stream:
            return None

        # Update is_live to true
        await streams_collection.update_one(
            {"stream_key": stream_key},
            {"$set": {"is_live": True}}
        )

        # Return minimal info
        return {
            "stream_id": stream["stream_id"],
            "is_live": True
        }
