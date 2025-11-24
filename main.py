from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from utils.cloudinary import cloudinary
from controllers.movie_controller import router as movie_router
from controllers.trailer_controller import router as trailer_router

load_dotenv()


app = FastAPI(
    title="Movie API",
    description="Handle Movie + Trailer Services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movie_router, prefix="/movies", tags=["Movies"])
app.include_router(trailer_router, prefix="/trailers", tags=["Trailers"])

@app.get("/")
def home():
    return {"message": "Movie API is running"}
