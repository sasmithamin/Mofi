from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["movie_db"]
collection = db["movies"]

# Cloudinary setup
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUD_API_KEY"),
    api_secret=os.getenv("CLOUD_API_SECRET")
)

@app.post("/movies")
async def upload_movie(
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    video: UploadFile = File(None)
):
    try:
        print("✅ Upload started:", title)

        image_url = None
        if image:
            print("Uploading image...")
            upload_result = cloudinary.uploader.upload(image.file, resource_type="image")
            image_url = upload_result.get("secure_url")

        video_url = None
        if video:
            print("Uploading video...")
            upload_result = cloudinary.uploader.upload(video.file, resource_type="video")
            video_url = upload_result.get("secure_url")

        movie_data = {
            "title": title,
            "description": description,
            "image_url": image_url,
            "video_url": video_url
        }
        result = collection.insert_one(movie_data)

        print("✅ Movie saved:", result.inserted_id)
        return {
            "id": str(result.inserted_id),
            "message": "Movie uploaded successfully!",
            "image_url": image_url,
            "video_url": video_url
        }

    except Exception as e:
        print("❌ Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
