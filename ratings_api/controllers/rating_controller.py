from fastapi import APIRouter, HTTPException, Form
from datetime import datetime, timezone
from ratings_api.db.mongo import pre_ratings_collection, post_ratings_collection, movies_collection

router = APIRouter()

@router.post("/ratings")
async def rate_movie(
    user_id: str = Form(...),
    movie_id: str = Form(...),
    stars: int = Form(...)
):
    if stars < 1 or stars > 5:
        raise HTTPException(status_code=400, detail="Stars must be between 1 and 5")

    movie = await movies_collection.find_one({"movie_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    now = datetime.now(timezone.utc)

    release_date_raw = movie["release_date"]
    if isinstance(release_date_raw, str):
        release_date = datetime.fromisoformat(
            release_date_raw.replace("Z", "+00:00")
        )
    else:
        release_date = release_date_raw

    if release_date.tzinfo is None:
        release_date = release_date.replace(tzinfo=timezone.utc)

    if now < release_date:
        rating_type = "pre"
        ratings_collection = pre_ratings_collection
        rate_key = "rate.pre"
    else:
        rating_type = "post"
        ratings_collection = post_ratings_collection
        rate_key = "rate.post"

    # 🔹 Check existing rating
    existing_user_rating = await ratings_collection.find_one(
        {
            "user_id": user_id,
            f"movies.{movie_id}": {"$exists": True}
        }
    )

    old_stars = None
    if existing_user_rating:
        old_stars = existing_user_rating["movies"][movie_id]["stars"]

    # 🔹 Save / replace rating
    await ratings_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"movies.{movie_id}": {
                    "stars": stars,
                    "rated_at": now,
                    "rate_type": rating_type
                }
            }
        },
        upsert=True
    )

    # 🔹 Update movie summary correctly
    if old_stars is not None:
        inc_ops = {f"{rate_key}.rate_vote": stars - old_stars}
    else:
        inc_ops = {
            f"{rate_key}.rate_vote": stars,
            f"{rate_key}.rate_count": 1
        }

    await movies_collection.update_one(
        {"movie_id": movie_id},
        {"$inc": inc_ops}
    )

    # 🔹 Recalculate average
    movie = await movies_collection.find_one({"movie_id": movie_id})
    rate_data = movie["rate"][rating_type]

    new_rate = (
        round(rate_data["rate_vote"] / rate_data["rate_count"], 2)
        if rate_data["rate_count"] > 0 else 0
    )

    await movies_collection.update_one(
        {"movie_id": movie_id},
        {"$set": {f"{rate_key}.rate": new_rate}}
    )

    return {
        "message": f"{rating_type.capitalize()} rating saved successfully",
        "stars": stars,
        "rate_summary": {
            "rate_vote": rate_data["rate_vote"],
            "rate_count": rate_data["rate_count"],
            "rate": new_rate
        }
    }

