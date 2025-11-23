import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUD_API_KEY"),
    api_secret=os.getenv("CLOUD_API_SECRET"),
)

def upload_image(upload_file, folder: str):
    file_bytes = upload_file.file.read()   

    return cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type="image"
    )["secure_url"]

