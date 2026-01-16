from movie_api.db.mongo import db
from movie_api.db.mongo import movies_collection
import uuid
from movie_api.schemas import MovieCreate, MovieUpdate
from typing import Optional
from bson import ObjectId
from datetime import datetime, timedelta


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
        "rate": movie.get("rate", {}),
        "reactions": movie.get("reactions", {}),
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

        movie_dict["rate"] = {
            "pre": {
                "rate_vote": 0,
                "rate_count": 0,
                "rate": 0
            },
            "post": {
                "rate_vote": 0,
                "rate_count": 0,
                "rate": 0
            }
        }

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
    
    @staticmethod
    async def update_movie_rating(
        movie_id: str,
        stars: int,
        is_new_rating: bool,
        old_stars: int | None = None
    ):
        movie = await movies_collection.find_one({"movie_id": movie_id})

        if not movie:
            raise Exception("Movie not found")

        rate = movie.get("rate")

        #  FORCE SAFE INITIALIZATION
        if not rate or rate.get("rate_count", 0) < 0:
            rate = {
                "rate_vote": 0,
                "rate_count": 0,
                "rate": 0.0
            }

        if is_new_rating:
            rate["rate_vote"] += stars
            rate["rate_count"] += 1
        else:
            if old_stars is not None:
                rate["rate_vote"] = rate["rate_vote"] - old_stars + stars

        #  SAFE AVERAGE CALCULATION
        rate["rate"] = round(
            rate["rate_vote"] / rate["rate_count"], 2
        ) if rate["rate_count"] > 0 else 0

        await movies_collection.update_one(
            {"movie_id": movie_id},
            {"$set": {"rate": rate}}
        )

    
    @staticmethod
    async def get_full_movie_details(movie_id: str) -> dict:
        movie = await db.movies.find_one({"movie_id": movie_id})
        if not movie:
            return None

        ratings = await db.ratings.find_one({"movie_id": movie_id})
        reactions = await db.reactions.find_one({"movie_id": movie_id})

        trailers = []
        async for trailer in db.trailers.find({"movie_id": movie_id}):
            trailer["trailer_id"] = str(trailer["_id"])
            trailer.pop("_id", None)
            trailers.append(trailer)

        stream = await db.streams.find_one({"movie_id": movie_id})

        # remove Mongo _id safely
        movie.pop("_id", None)
        if ratings: ratings.pop("_id", None)
        if reactions: reactions.pop("_id", None)
        if stream: stream.pop("_id", None)

        return {
            "movie": movie,
            "ratings": ratings or {},
            "reactions": reactions or {},
            "trailers": trailers,
            "stream": stream or {}
        }
    
    @staticmethod
    async def get_coming_soon_movies() -> list:
        movies = []

        async for movie in db.movies.find({}):
            release_date = movie.get("release_date")

            if not release_date:
                continue

        # coming soon window = release_date → release_date + 30 days
        coming_soon_until = release_date + timedelta(days=30)

        movie["coming_soon"] = {
            "from": release_date,
            "to": coming_soon_until
        }

        movies.append(serialize_movie(movie))

        return movies
    
    @staticmethod
    async def get_released_movies() -> list:
        today = datetime.utcnow()

        movies = []

        async for movie in db.movies.find({
            "release_date": {"$lte": today}
        }):
            movies.append(serialize_movie(movie))

        return movies
    
    @staticmethod
    async def get_trending_movies(limit: int = 10):
        """
        Trending movies based on highest PRE rating count
        """

        cursor = (
            movies_collection
            .find(
                {"rate.pre.rate_count": {"$gt": 0}},
                {
                    "_id": 0,
                    "movie_id": 1,
                    "title": 1,
                    "description": 1,
                    "image1": 1,
                    "image2": 1,
                    "release_date": 1,
                    "rate.pre.rate_count": 1,
                    "rate.pre.rate": 1
                }
            )
            .sort("rate.pre.rate_count", -1)
            .limit(limit)
        )

        movies = await cursor.to_list(length=limit)

        return [
            {
                "movie_id": m["movie_id"],
                "title": m["title"],
                "description": m.get("description"),
                "image1": m.get("image1"),
                "image2": m.get("image2"),
                "release_date": m.get("release_date"),
                "pre_rate_count": m["rate"]["pre"]["rate_count"],
                "pre_rate_avg": m["rate"]["pre"].get("rate", 0)
            }
            for m in movies
        ]
    
    @staticmethod
    async def get_popular_movies(limit: int = 10):
        """
        Popular movies / series / anime based on highest POST rating count
        """

        cursor = (
            db.movies
            .find(
                {"rate.post.rate_count": {"$gt": 0}},
                {
                    "_id": 0,
                    "movie_id": 1,
                    "title": 1,
                    "description": 1,
                    "image1": 1,
                    "image2": 1,
                    "release_date": 1,
                    "type": 1,
                    "rate.post.rate_count": 1,
                    "rate.post.rate": 1
                }
            )
            .sort("rate.post.rate_count", -1)
            .limit(limit)
        )

        movies = await cursor.to_list(length=limit)

        return [
            {
                "movie_id": m["movie_id"],
                "type": m.get("type"),
                "title": m.get("title"),
                "description": m.get("description"),
                "image1": m.get("image1"),
                "image2": m.get("image2"),
                "release_date": m.get("release_date"),
                "post_rate_count": m["rate"]["post"]["rate_count"],
                "post_rate_avg": m["rate"]["post"].get("rate", 0)
            }
            for m in movies
        ]
