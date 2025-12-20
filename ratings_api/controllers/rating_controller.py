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
    # Validate stars
    if stars < 1 or stars > 5:
        raise HTTPException(status_code=400, detail="Stars must be between 1 and 5")

    # Fetch the movie
    movie = await movies_collection.find_one({"movie_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Current UTC time (timezone-aware)

    #now = datetime(2025, 12, 31, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    release_date_raw = movie["release_date"]  # must be timezone-aware

    # If release_date is STRING → convert to datetime
    if isinstance(release_date_raw, str):
        release_date = datetime.fromisoformat(
        release_date_raw.replace("Z", "+00:00")
        )
    else:
        release_date = release_date_raw

    # Force timezone awareness (safety)
    if release_date.tzinfo is None:
        release_date = release_date.replace(tzinfo=timezone.utc)

    # Determine pre or post rating
    if now < release_date:
        rating_type = "pre"
        ratings_collection = pre_ratings_collection
        rate_key = "rate.pre"
    else:
        rating_type = "post"
        ratings_collection = post_ratings_collection
        rate_key = "rate.post"

    # Insert rating (no unique constraint; same user can rate multiple times for now)
    await ratings_collection.insert_one({
        "user_id": user_id,
        "movie_id": movie_id,
        "stars": stars,
        "rated_at": now,
        "rate_type": rating_type
    })

    # Update movie summary: increment vote sum and count
    await movies_collection.update_one(
        {"movie_id": movie_id},
        {
            "$inc": {
                f"{rate_key}.rate_vote": stars,
                f"{rate_key}.rate_count": 1
            }
        }
    )

    # Recalculate average
    movie = await movies_collection.find_one({"movie_id": movie_id})
    rate_data = movie["rate"][rating_type]
    new_rate = round(rate_data["rate_vote"] / rate_data["rate_count"], 2) if rate_data["rate_count"] > 0 else 0

    await movies_collection.update_one(
        {"movie_id": movie_id},
        {
            "$set": {f"{rate_key}.rate": new_rate}
        }
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
