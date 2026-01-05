from fastapi import APIRouter, UploadFile, File, Form,  HTTPException
from movie_api.services.movie_service import MovieService
from movie_api.utils.cloudinary import upload_image
from movie_api.schemas import MovieCreate, MovieUpdate
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=dict)
async def create_movie(
    user_id: str =  Form(...),
    imdbID: str = Form(...),
    type: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    directors: str = Form(...),
    writers: str = Form(...),
    genres: str = Form(...),
    release_date: datetime = Form(...),
    duration: str = Form(...),
    image1: UploadFile = File(...),
    image2: UploadFile = File(...)
):

    img1_url = upload_image(image1, "movie_db/movies")
    img2_url = upload_image(image2, "movie_db/movies")

    movie_data = MovieCreate(
        user_id=user_id,
        imdbID=imdbID,
        type=type,
        title=title,
        description=description,
        directors=directors.split(","), 
        writers=writers.split(","),
        genres=genres.split(","),
        release_date=release_date,
        duration=duration,
        image1=img1_url,
        image2=img2_url
    )

    movie = await MovieService.create_movie(movie_data)
    return {"message": "Movie created successfully", "movie": movie}

@router.get("/", response_model=list)
async def get_all_movies():
    return await MovieService.get_all_movies()

@router.get("/{movie_id}", response_model=dict)
async def get_movie(movie_id: str):
    movie = await MovieService.get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.put("/{movie_id}", response_model=dict)
async def update_movie(
    movie_id: str,
    user_id:Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    directors: Optional[str] = Form(None),
    writers: Optional[str] = Form(None),
    genres: Optional[str] = Form(None),
    release_date: Optional[str] = Form(None),
    duration: Optional[str] = Form(None),
    image1: Optional[UploadFile] = File(None),
    image2: Optional[UploadFile] = File(None)
):
    update_data = MovieUpdate()

    if title: update_data.title = title
    if description: update_data.description = description
    if directors: update_data.directors = directors.split(",")
    if writers: update_data.writers = writers.split(",")
    if genres: update_data.genres = genres.split(",")
    if release_date: update_data.release_date = release_date
    if duration: update_data.duration = duration
    if user_id: update_data.user_id = user_id

    if image1:
        update_data.image1 = await upload_image(image1, "movie_db/movies")
    if image2:
        update_data.image2 = await upload_image(image2, "movie_db/movies")

    updated = await MovieService.update_movie(movie_id, update_data)

    if not updated:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {"message": "Movie updated successfully", "movie": updated}

@router.delete("/{movie_id}", response_model=dict)
async def delete_movie(movie_id: str):
    deleted = await MovieService.delete_movie(movie_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deleted successfully"}

@router.get("/user/{user_id}", response_model=list)
async def get_movies_by_user(user_id: str):
    return await MovieService.get_movies_by_user(user_id)


@router.get("/{movie_id}/full", response_model=dict)
async def get_full_movie(movie_id: str):
    data = await MovieService.get_full_movie_details(movie_id)

    if not data:
        raise HTTPException(status_code=404, detail="Movie not found")

    return data