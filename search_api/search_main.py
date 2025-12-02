from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from search_api.controllers.search_controller import router as search_router

app = FastAPI(
    title="Movie Search API",
    description="Search movies by title",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(search_router)

@app.get("/")
def home():
    return {"message": "Search API is running"}

