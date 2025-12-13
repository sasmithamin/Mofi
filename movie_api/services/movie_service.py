from movie_api.db.mongo import db
import uuid
from movie_api.schemas import MovieCreate, MovieUpdate
from typing import Optional
from bson import ObjectId


def serialize_movie(movie):
    return {
        "movie_id": movie["movie_id"],
        "user_id": movie["user_id"],
        "imdbID": movie["imdbID"],
        "type": movie["type"],
        "title": movie["title"],
        "description": movie["description"],
        "directors": movie["directors"],
        "writers": movie["writers"],
        "genres": movie["genres"],
        "release_date": movie["release_date"],
        "duration": movie["duration"],
        "image1": movie["image1"],
        "image2": movie["image2"],
    }


class MovieService:
    @staticmethod
    async def create_movie(movie_data: MovieCreate) -> dict:
        movie_dict = movie_data.model_dump()

        existing = await db.movies.find_one(
            {"imdbID": movie_dict["imdbID"]}
        )
        if existing:
            raise Exception("Movie with this IMDb ID already exists")
        
        movie_dict["movie_id"] = str(uuid.uuid4())

        await db.movies.insert_one(movie_dict)

        return serialize_movie(movie_dict)


    @staticmethod
    async def get_all_movies() -> list:
        movies = []
        async for movie in db.movies.find():
            movies.append(serialize_movie(movie))
        return movies


    @staticmethod
    async def get_movie(movie_id: str) -> Optional[dict]:
        movie = await db.movies.find_one({"movie_id": movie_id})

        if movie:
            return serialize_movie(movie)

        return None


    @staticmethod
    async def update_movie(movie_id: str, update_data: MovieUpdate) -> Optional[dict]:
        update_fields = {
            key: value
            for key, value in update_data.model_dump().items()
            if value is not None
        }

        if not update_fields:
            return None

        result = await db.movies.update_one(
            {"movie_id": movie_id},
            {"$set": update_fields}
        )

        if result.modified_count == 0:
            return None

        updated_movie = await db.movies.find_one({"movie_id": movie_id})
        return serialize_movie(updated_movie)


    @staticmethod
    async def delete_movie(movie_id: str) -> bool:
        result = await db.movies.delete_one({"movie_id": movie_id})
        return result.deleted_count == 1
    
    @staticmethod
    async def get_movies_by_user(user_id: str) -> list:
        movies = []
        async for movie in db.movies.find({"user_id": user_id}):
            movies.append(serialize_movie(movie))
        return movies

