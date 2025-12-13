from fastapi import APIRouter, HTTPException, Query
from search_api.services.search_service import SearchService
from search_api.db.mongo import movies_collection
from search_api.utils.serializer import serialize_mongo

router = APIRouter()

#filter by name
@router.get("/search/by-name")
async def search_by_movie_name(
    moviename: str = Query(..., description="Movie name keyword")
):
    try:
        results = await movies_collection.find(
            {"title": {"$regex": moviename, "$options": "i"}}
        ).to_list(100)

        return {
            "count": len(results),
            "results": serialize_mongo(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#filter by type  
@router.get("/search/by-type")
async def search_by_type(
    type: str = Query(..., description="movie | series | anime")
):
    try:
        results = await movies_collection.find(
            {"type": type.lower()}
        ).to_list(100)

        return {
            "count": len(results),
            "results": serialize_mongo(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))