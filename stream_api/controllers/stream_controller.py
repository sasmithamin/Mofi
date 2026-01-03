from fastapi import APIRouter, HTTPException, Form
from stream_api.services.stream_service import StreamService
from stream_api.db.mongo import streams_collection
from stream_api.utils.serializer import serialize_mongo

router = APIRouter(prefix="/streams", tags=["Streams"])


@router.post("/")
async def create_stream(
    user_id: str = Form(...),
    movie_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    date_time: str = Form(...),  # human-readable
    is_live: bool = Form(False)
):
    try:
        stream = await StreamService.create_stream(
            user_id=user_id,
            movie_id=movie_id,
            title=title,
            description=description,
            date_time=date_time,
            is_live=is_live
        )
        return stream

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_all_streams():
    try:
        return await StreamService.get_all_streams()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{stream_id}")
async def delete_stream(stream_id: str):
    try:
        deleted = await StreamService.delete_stream(stream_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Stream not found")
        return {"message": "Stream deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.get("/streams/validate/{stream_key}")
async def validate_stream_key(stream_key: str):
    try:
        result = await StreamService.validate_stream_key(stream_key)

        if not result:
            return {
                "valid": False,
                "message": "Invalid stream key"
            }

        return {
            "valid": True,
            "message": "Stream key validated",
            "stream_id": result["stream_id"],
            "is_live": result["is_live"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/streams/active")
async def get_active_streams():
    streams = await streams_collection.find({"is_live": True}).to_list(100)
    safe_streams = serialize_mongo(streams)  
    return {"count": len(safe_streams), "results": safe_streams}

