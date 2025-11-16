from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Body
from pymongo import MongoClient
from bson import ObjectId
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
import random
import string
import uuid
from typing import Optional
from datetime import datetime

#load env variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
CLOUD_NAME = os.getenv("CLOUD_NAME")
CLOUD_API_KEY = os.getenv("CLOUD_API_KEY")
CLOUD_API_SECRET = os.getenv("CLOUD_API_SECRET")

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["movie_db"]
collection = db["movies"]
search_logs = db["search_logs"]

# Cloudinary setup
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUD_API_KEY"),
    api_secret=os.getenv("CLOUD_API_SECRET")
)

#generate movie id
def generate_movie_id():
    return "MOV-" + str(uuid.uuid4())


def movie_serializer(movie) -> dict:
    return {
        "id": str(movie["_id"]),
        "movie_id": movie.get("movie_id"),
        "title": movie.get("title"),
        "description": movie.get("description"),
        "images": movie.get("images"),
        "directors": movie.get("directors"),
        "writers": movie.get("writers"),
        "genres": movie.get("genres"),
        "release_date": movie.get("release_date"),
        "duration": movie.get("duration"),
        "trailers": [
             {
                  "trailer_name": t.get("trailer_name"),
                  "thumbnail_url": t.get("thumbnail_url"),
                  "video_url": t.get("video_url")
             }
             for t in movie.get("trailers", [])
        ]
    }

 #add movies   
@app.post("/movies")
async def add_movie(
    title: str = Form(...),
    description: str = Form(...),
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    directors: str = Form(...),
    writers: str = Form(...),
    genres: str =  Form(...),
    release_date: str = Form(...),
    duration: str = Form(...)
):
    try:
        #upload images to cludinary
        image1_upload = cloudinary.uploader.upload(image1.file, folder="movie_images", resource_type="image")
        image2_upload = cloudinary.uploader.upload(image2.file, folder="movie_images", resource_type="image")

        #new movie document
        new_movie = {
            "movie_id": generate_movie_id(),
            "title": title,
            "description": description,
            "images": [image1_upload["secure_url"], image2_upload["secure_url"]],
            "directors": directors,
            "writers": writers,
            "genres": genres.split(","),
            "release_date": release_date,
            "duration": duration,
            "trailers": []
        }

        result = collection.insert_one(new_movie)

        return {
            "id": str(result.inserted_id),
            "movie_id": new_movie["movie_id"],
            "message": "Movie added successfully"
        }

    except Exception as e:
           raise HTTPException(status_code=500, detail=str(e)) 


#add trailer
@app.post("/trailer")
async def add_trailer(
     movie_id: str = Form(...),
     trailer_name: str = Form(...),
     thumbnail: UploadFile = File(...),
     video: UploadFile = File(...)
):
     try:
          movie = collection.find_one({"movie_id": movie_id})
          if not movie:
               raise HTTPException(status_code=404, detail="Movie not found")
          
          #cloudinary upload
          thumbnail_upload = cloudinary.uploader.upload(thumbnail.file, folder="trailer_thumbnails", resource_type="image")
          video_upload = cloudinary.uploader.upload(video.file, folder="trailer_videos", resource_type="video")

          trailer_data =  {
               "trailer_name": trailer_name,
               "thumbnail_url": thumbnail_upload["secure_url"],
               "video_url": video_upload["secure_url"]       
            }

          collection.update_one(
               {"movie_id": movie_id},
               {"$push": {"trailers": trailer_data}}
          )

          return {"message": "Trailer added succcessfully"}
     
     except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
     
#show movie  details
@app.get("/movies")
def get_movies():
     movies = list(collection.find())
     return [movie_serializer(m) for m in movies]
     
#update only movie form type data   
@app.patch("/movies/{movie_id}")
async def update_movie(
     movie_id: str,
     update_data: dict = Body(...)
):
     
     movie = collection.find_one({"movie_id": movie_id})
     if  not movie:
          raise HTTPException(status_code=404, detail="Movie not found")
     
     allowed_fields = {
          "title",
          "description",
          "directors",
          "writers",
          "genres",
          "release_date",
          "duration",
          "trailer_name"
     }
     
     clean_update = {k: v for k, v in update_data.items() if k in allowed_fields}

     if not clean_update:
          raise HTTPException(status_code=400, detail="No valid fields provided")
     
     if "trailer_name" in clean_update:
        trailers = movie.get("trailers", [])
        if trailers:
            trailers[0]["trailer_name"] = clean_update.pop("trailer_name")
            clean_update["trailers"] = trailers
        else:
            clean_update["trailers"] = [{"trailer_name": update_data["trailer_name"]}]
     
     collection.update_one({"movie_id": movie_id}, {"$set": update_data})

     return {"message": f"Movie {movie_id} text fileds updated successfully"}     


#update movie images
@app.patch("/movies/{movie_id}/images")
async def update_movie_images(
     movie_id: str,
     image1: UploadFile = File(None),
     image2: UploadFile = File(None),
):
     movie = collection.find_one({"movie_id": movie_id})
     if not movie:
          raise HTTPException(status_code=404, detail="Movie not found")
     
     update_data = {}

     if image1:
          if movie.get("image1_url"):
               public_id = movie["image1_url"].split("/")[-1].split(".")[0]
               cloudinary.uploader.destroy(public_id, resource_type="image")
          
          upload_result = cloudinary.uploader.upload(image1.file, resource_type="image", folder="movie_images")
          update_data["image1_url"] = upload_result["secure_url"]

     if image2:
          if movie.get("image2_url"):
               public_id = movie["image2_url"].split("/")[-1].split(".")[0]
               cloudinary.uploader.destroy(public_id, resource_type="image")

          upload_result = cloudinary.uploader.upload(image2.file, resource_type="image", folder="movie_images")
          update_data["image2_url"] = upload_result["secure_url"]
     
     if not update_data:
          raise HTTPException(status_code=400, detail="No images provided")
     
     collection.update_one({"movie_id": movie_id}, {"$set": update_data})

     return {"message": "Image(s) updated successfully", "updated": update_data}
     

#update trailer media
@app.patch("/movies/{movie_id}/trailer")
async def update_trailers(
     movie_id: str,
     trailer_thumbnail: Optional[UploadFile] = File(None),
     trailer_video: Optional[UploadFile] = File(None)
):
     
     movie = collection.find_one({"movie_id": movie_id})
     if not movie:
          raise HTTPException(status_code=404,  detail="Movie not found")
     
     trailers = movie.get("trailers", [])
     if not trailers:
          raise HTTPException(status_code=400, detail="No trailer found")
     
     trailer = trailers[0]

     update_data = {}

     if trailer_thumbnail:
          if trailer.get("thumbnail_url"):
               public_id = trailer["thumbnail_url"].split("/")[-1].split(".")[0]
               cloudinary.uploader.destroy(public_id, resource_type="image")

          thumb_upload = cloudinary.uploader.upload(
               trailer_thumbnail.file,
               resource_type="image",
               folder="trailer_thumbnails"
          )
          trailer["thumbnail_url"] = thumb_upload["secure_url"]

     if trailer_video:
          if trailer.get("video_url"):
               public_id = trailer["video_url"].split("/")[-1].split(".")[0]
               cloudinary.uploader.destroy(public_id, resource_type="video")
          
          video_upload = cloudinary.uploader.upload(
               trailer_video.file,
               resource_type="video",
               folder="trailer_videos"
          )
          trailer["video_url"] = video_upload["secure_url"]
     
     update_data["trailers"] = trailers

     collection.update_one(
          {"movie_id": movie_id},
          {"$set": update_data}
     )
     
     return {
          "message": "Trailer updated successfully",
          "updated_trailer": trailer
     }

@app.delete("/movies/{movie_id}")
async def delete_movie(movie_id: str):
     movie = collection.find_one({"movie_id": movie_id})
     if not movie:
          raise HTTPException(status_code=404, detail="Movie not found")
     
     result =collection.delete_one({"movie_id": movie_id})
     if result.deleted_count == 1:
          return {"message": f"Movie {movie_id} deleted successfully"}
     raise HTTPException(status_code=500, detail="Failed to delete")
     

@app.get("/movies/search")
def search_movies(query: str):
    
    if query.strip():
         search_logs.insert_one({
              "query": query.lower(),
              "timestamp": datetime.utcnow()
         })

    movies = list(collection.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"trailers.trailer_name": {"$regex": query, "$options": "i"}}
        ]
    }).limit(10)) #limit to 10 results

    return [movie_serializer(m) for m in movies]


@app.get("/movies/most-searched")
def most_searched_movies(limit: int = 10):
    pipeline = [
        {"$group": {"_id": "$query", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]

    keyword_counts = list(search_logs.aggregate(pipeline))

    result = []
    for item in keyword_counts:
        keyword = item["_id"]
        count = item["count"]

        movies = list(collection.find({
            "title": {"$regex": keyword, "$options": "i"}
        }))

        for m in movies:
            result.append({
                "keyword": keyword,
                "count": count,
                "movies": movie_serializer(m)
            })

    return result



          