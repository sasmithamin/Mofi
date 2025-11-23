from pydantic import BaseModel, Field
from typing import Optional, List

class MovieBase(BaseModel):
    title: str
    description: str
    directors: List[str]
    writers: List[str]
    genres: List[str]
    release_date: int
    duration: str

class MovieCreate(MovieBase):
    image1: str
    image2: str

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    directors: Optional[List[str]] = None
    writers: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    release_date: Optional[int] = None
    duration: Optional[str] = None
    image1: Optional[str] = None
    image2: Optional[str] = None

class Movie(MovieBase):
    movie_id: str
    image1: str
    image2: str

    class Config:
        orm_mode = True




