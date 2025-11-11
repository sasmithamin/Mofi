from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pymongo import MongoClient
from bson import ObjectId
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
import random
import string
import uuid

#load env variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
CLOUD_NAME = os.getenv("CLOUD_NAME")
CLOUD_API_KEY = os.getenv("CLOUD_API_KEY")
CLOUD_API_SECRET = os.getenv("CLOUD_API_SECRET")

app = FastAPI()

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["movie_db"]
collection = db["movies"]

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
        "trailers": []
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
     

@app.get("/movies")
def get_movies():
     movies = list(collection.find())
     return [movie_serializer(m) for m in movies]
     
     


          