from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime

class MovieBase(BaseModel):
    imdbID: str
    type: str
    title: str
    description: str
    directors: List[str]
    writers: List[str]
    genres: List[str]
    release_date: datetime
    duration: str

class MovieCreate(MovieBase):
    user_id: str
    image1: str
    image2: str

class MovieUpdate(BaseModel):
    imdbID: Optional[str] = None
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    directors: Optional[List[str]] = None
    writers: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    release_date: Optional[datetime] = None
    duration: Optional[str] = None
    user_id: Optional[str] = None
    image1: Optional[str] = None
    image2: Optional[str] = None

class Movie(MovieBase):
    movie_id: str
    user_id: str
    image1: str
    image2: str

    rate: Dict[str, float] = {}
    reactions: Dict[str, int] = {}

    class Config:
        orm_mode = True

class TrailerCreate(BaseModel):
    movie_id: str
    trailer_name: str
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None

class TrailerUpdate(BaseModel):
    trailer_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None

class Trailer(BaseModel):
    trailer_id: str
    movie_id: str
    trailer_name: str
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None

    class Config:
        orm_mode = True
