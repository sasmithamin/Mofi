from fastapi import APIRouter, HTTPException, Form
from datetime import datetime, timezone
from typing import Optional

from reaction_api.schemas.reaction_schema import ReactionEnum, PreferenceEnum
from reaction_api.db.mongo import movies_collection, reactions_collection

router = APIRouter()


@router.post("/reactions")
async def add_reaction(
    user_id: str = Form(...),
    movie_id: str = Form(...),

    # ✅ DROPDOWNS IN SWAGGER
    reaction: Optional[ReactionEnum] = Form(None),
    preference: Optional[PreferenceEnum] = Form(None),
):
    movie = await movies_collection.find_one({"movie_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Save raw reaction
    await reactions_collection.insert_one({
        "user_id": user_id,
        "movie_id": movie_id,
        "reaction": reaction.value if reaction else None,
        "preference": preference.value if preference else None,
        "created_at": datetime.now(timezone.utc)
    })

    updates = {}

    if reaction:
        updates[f"reactions.emoji_reactions.{reaction.name}"] = 1

    if preference:
        updates[f"reactions.preferences.{preference.value}"] = 1

    if updates:
        await movies_collection.update_one(
            {"movie_id": movie_id},
            {"$inc": updates}
        )

    return {
        "message": "Reaction saved successfully",
        "reaction": reaction.value if reaction else None,
        "preference": preference.value if preference else None
    }
