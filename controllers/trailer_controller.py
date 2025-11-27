from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from services.trailer_service import TrailerService
from utils.cloudinary import upload_image, upload_video
from schemas import TrailerCreate, TrailerUpdate, Trailer

router = APIRouter(prefix="/trailers", tags=["Trailers"])


@router.post("/", response_model=dict)
async def create_trailer(
    movie_id: str = Form(...),
    trailer_name: str = Form(...),
    thumbnail: UploadFile = File(...),
    video: UploadFile = File(...)
):
    # Upload thumbnail + video
    thumbnail_url = upload_image(thumbnail, "movie_db/trailers")
    video_url = upload_video(video, "movie_db/trailers")

    # Create Pydantic model
    trailer_data = TrailerCreate(
        movie_id=movie_id,
        trailer_name=trailer_name,
        thumbnail_url=thumbnail_url,
        video_url=video_url
    )

    # IMPORTANT FIX → convert to dict
    trailer = await TrailerService.create_trailer(trailer_data)

    return {"message": "Trailer created successfully", "trailer": trailer}


@router.get("/{trailer_id}", response_model=Trailer)
async def get_one(trailer_id: str):
    trailer = await TrailerService.get_trailer_by_id(trailer_id)
    if not trailer:
        raise HTTPException(status_code=404, detail="Trailer not found")
    return trailer


@router.put("/{trailer_id}", response_model=dict)
async def update_trailer(
    trailer_id: str,
    trailer_name: Optional[str] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None)
):
    update_data = TrailerUpdate()

    if trailer_name:
        update_data.trailer_name = trailer_name
    if thumbnail:
        update_data.thumbnail_url = upload_image(thumbnail, "movie_db/trailers")
    if video:
        update_data.video_url = upload_video(video, "movie_db/trailers")

    # Convert Pydantic model → dict
    updated = await TrailerService.update_trailer(trailer_id, update_data)

    if not updated:
        raise HTTPException(status_code=404, detail="Trailer not found")

    return {"message": "Trailer updated successfully", "trailer": updated}


@router.delete("/{trailer_id}", response_model=dict)
async def delete_trailer(trailer_id: str):
    deleted = await TrailerService.delete_trailer(trailer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trailer not found")
    return {"message": "Trailer deleted successfully"}
