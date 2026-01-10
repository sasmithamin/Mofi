from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Path
from typing import Optional, List
from uuid import uuid4
from movie_api.db.mongo import db
from datetime import datetime
from movie_api.services.trailer_service import TrailerService
from movie_api.utils.cloudinary import upload_image, upload_video
from movie_api.schemas import TrailerCreate, TrailerUpdate, Trailer

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

@router.get("/movie/{movie_id}", response_model=List[Trailer])
async def get_trailers_by_movie(movie_id: str):
    trailers = await TrailerService.get_trailers_by_movie_id(movie_id)
    return trailers


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


@router.post("/{movie_id}/production-images")
async def add_trailer_production_image(
    movie_id: str = Path(..., description="Movie ID"),
    image: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...)
):
    # 1. Validate movie exists
    movie = await db.movies.find_one({"movie_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # 2. Upload image to Cloudinary
    image_url = upload_image(
        image,
        folder=f"movie_db/trailers/{movie_id}/production_images"
    )

    # 3. Save metadata in MongoDB
    image_doc = {
        "image_id": str(uuid4()),
        "movie_id": movie_id,
        "title": title,
        "description": description,
        "image_url": image_url,
        "created_at": datetime.utcnow()
    }

    await db.trailer_production_images.insert_one(image_doc)
    image_doc.pop("_id", None)

    return {
        "message": "Trailer production image uploaded successfully",
        "data": image_doc
    }