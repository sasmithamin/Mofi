from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stream_api.controllers.stream_controller import router as stream_router

app = FastAPI(
    title="Live Stream API",
    description="Create and manage movie live streams",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(stream_router)

@app.get("/")
def home():
    return {"message": "Stream API is running"}
