from fastapi import APIRouter, HTTPException, Form
from stream_api.services.stream_service import StreamService
from stream_api.db.mongo import streams_collection
from typing import Optional
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
    
    
@router.post("/stream/start")
async def start_stream(stream_key: str = Form(...)):
    result = await StreamService.start_stream(stream_key)

    if not result:
        raise HTTPException(status_code=404, detail="Invalid stream key")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/stream/stop")
async def stop_stream(stream_key: str = Form(...)):
    result = await StreamService.stop_stream(stream_key)

    if not result:
        raise HTTPException(status_code=404, detail="Invalid stream key")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
    

@router.get("/streams/active")
async def get_active_streams():
    streams = await streams_collection.find({"is_live": True}).to_list(100)
    safe_streams = serialize_mongo(streams)  
    return {"count": len(safe_streams), "results": safe_streams}

@router.put("/streams/{stream_id}")
async def update_stream(
    stream_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    date_time: Optional[str] = Form(None)
):
    updated_stream = await StreamService.update_stream(
        stream_id=stream_id,
        title=title,
        description=description,
        date_time=date_time
    )

    if not updated_stream:
        raise HTTPException(status_code=404, detail="Stream not found or no data to update")

    return {
        "message": "Stream updated successfully",
        "stream": updated_stream
    }

