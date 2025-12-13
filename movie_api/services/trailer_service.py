import uuid
from typing import Optional, List
from bson import ObjectId
from movie_api.db.mongo import db
from movie_api.schemas import TrailerCreate, TrailerUpdate

trailer_collection = db["trailers"]


def serialize_trailer(tr):
    return {
        "trailer_id": tr["trailer_id"],
        "movie_id": tr["movie_id"],
        "trailer_name": tr["trailer_name"],
        "thumbnail_url": tr.get("thumbnail_url"),
        "video_url": tr.get("video_url"),
    }


class TrailerService:

    @staticmethod
    async def create_trailer(data: TrailerCreate):
        trailer_dict = data.model_dump()
        trailer_dict["trailer_id"] = str(uuid.uuid4())   # <-- custom ID like movies

        await trailer_collection.insert_one(trailer_dict)

        return serialize_trailer(trailer_dict)

    @staticmethod
    async def get_trailer_by_id(trailer_id: str):
        trailer = await trailer_collection.find_one({"trailer_id": trailer_id})
        if trailer:
            return serialize_trailer(trailer)
        return None
    
    @staticmethod
    async def get_trailers_by_movie_id(movie_id: str):
        trailers = await trailer_collection.find({"movie_id": movie_id}).to_list(None)
        return [await TrailerService.to_trailer_dict(t) for t in trailers]

    @staticmethod
    async def get_all_trailers():
        trailers = []
        async for tr in trailer_collection.find():
            trailers.append(serialize_trailer(tr))
        return trailers

    @staticmethod
    async def update_trailer(trailer_id: str, update_data: TrailerUpdate):
        update_fields = {
            key: value
            for key, value in update_data.model_dump().items()
            if value is not None
        }

        if not update_fields:
            return None

        result = await trailer_collection.update_one(
            {"trailer_id": trailer_id},
            {"$set": update_fields}
        )

        if result.modified_count == 0:
            return None

        updated = await trailer_collection.find_one({"trailer_id": trailer_id})
        return serialize_trailer(updated)

    @staticmethod
    async def delete_trailer(trailer_id: str) -> bool:
        result = await trailer_collection.delete_one({"trailer_id": trailer_id})
        return result.deleted_count == 1
