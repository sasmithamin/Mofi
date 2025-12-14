from fastapi import APIRouter, HTTPException, Form
from ratings_api.db.mongo import ratings_collection

router = APIRouter()

@router.post("/ratings")
async def add_rating(
    user_id: str = Form(...),
    movie_id: str = Form(...),
    stars: int = Form(...)
):
    try:
        # Check if user document exists
        user_ratings = await ratings_collection.find_one({"user_id": user_id})

        if user_ratings:
            # Check if movie already rated
            existing_movie = next(
                (r for r in user_ratings["ratings"] if r["movie_id"] == movie_id),
                None
            )

            if existing_movie:
                # Update existing movie rating
                await ratings_collection.update_one(
                    {
                        "user_id": user_id,
                        "ratings.movie_id": movie_id
                    },
                    {
                        "$set": {"ratings.$.stars": stars}
                    }
                )
            else:
                # Add new movie rating
                await ratings_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$push": {
                            "ratings": {
                                "movie_id": movie_id,
                                "stars": stars
                            }
                        }
                    }
                )
        else:
            # Create new user document
            await ratings_collection.insert_one({
                "user_id": user_id,
                "ratings": [
                    {
                        "movie_id": movie_id,
                        "stars": stars
                    }
                ]
            })

        return {"message": "Rating saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
