from fastapi import APIRouter, HTTPException, Query
from search_api.services.search_service import SearchService
from search_api.db.mongo import movies_collection
from search_api.utils.serializer import serialize_mongo

router = APIRouter()

@router.get("/search")
async def search_movies(query: str):
    try:
        results = await movies_collection.find(
            {"title": {"$regex": query, "$options": "i"}}
        ).to_list(100)

        # Convert ALL MongoDB documents to JSON-safe format
        safe_results = serialize_mongo(results)

        return {"results": safe_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

