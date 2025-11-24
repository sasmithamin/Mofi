from typing import List, Optional
from schemas import TrailerCreate, TrailerUpdate, Trailer
from bson import ObjectId
from db.mongo import db  

trailer_collection = db["trailers"]

class TrailerService:

    @staticmethod
    async def create_trailer(trailer_data: TrailerCreate) -> Trailer:
        trailer_dict = trailer_data.dict()
        result = await trailer_collection.insert_one(trailer_dict)

        trailer_dict["trailer_id"] = str(result.inserted_id)
        return Trailer(**trailer_dict)

    @staticmethod
    async def get_trailers(movie_id: str) -> List[Trailer]:
        cursor = trailer_collection.find({"movie_id": movie_id})
        trailers = []

        async for doc in cursor:
            doc["trailer_id"] = str(doc["_id"])
            doc.pop("_id", None)
            trailers.append(Trailer(**doc))

        return trailers

    @staticmethod
    async def update_trailer(trailer_id: str, update_data: TrailerUpdate) -> Optional[Trailer]:
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

        result = await trailer_collection.update_one(
            {"_id": ObjectId(trailer_id)},
            {"$set": update_dict}
        )

        if result.matched_count == 0:
            return None

        updated = await trailer_collection.find_one({"_id": ObjectId(trailer_id)})
        updated["trailer_id"] = str(updated["_id"])
        updated.pop("_id", None)
        return Trailer(**updated)

    @staticmethod
    async def delete_trailer(trailer_id: str) -> bool:
        result = await trailer_collection.delete_one({"_id": ObjectId(trailer_id)})
        return result.deleted_count > 0
