from fastapi import APIRouter, HTTPException, Form
from ratings_api.db.mongo import ratings_collection
from ratings_api.schemas.rating_schema import RatingCreate
from movie_api.services.movie_service import MovieService

router = APIRouter()

@router.post("/ratings")
async def add_rating(
    user_id: str = Form(...),
    movie_id: str = Form(...),
    stars: int = Form(...)
):
    try:
        if stars < 1 or stars > 5:
            raise HTTPException(status_code=400, detail="Stars must be between 1 and 5")

        user_ratings = await ratings_collection.find_one({"user_id": user_id})

        is_new_rating = True
        old_stars = None

        if user_ratings:
            for rating in user_ratings.get("ratings", []):
                if rating["movie_id"] == movie_id:
                    is_new_rating = False
                    old_stars = rating["stars"]
                    break

        # --- Save user rating ---
        if is_new_rating:
            if user_ratings:
                await ratings_collection.update_one(
                    {"user_id": user_id},
                    {"$push": {"ratings": {"movie_id": movie_id, "stars": stars}}}
                )
            else:
                await ratings_collection.insert_one({
                    "user_id": user_id,
                    "ratings": [{"movie_id": movie_id, "stars": stars}]
                })
        else:
            await ratings_collection.update_one(
                {"user_id": user_id, "ratings.movie_id": movie_id},
                {"$set": {"ratings.$.stars": stars}}
            )

        # ⭐ Update movie rating (single source of truth)
        await MovieService.update_movie_rating(
            movie_id=movie_id,
            stars=stars,
            old_stars=old_stars,
            is_new_rating=is_new_rating
        )

        return {
            "message": "Rating saved",
            "is_new_rating": is_new_rating,
            "old_stars": old_stars,
            "new_stars": stars
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

