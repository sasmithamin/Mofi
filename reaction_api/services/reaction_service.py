from reaction_api.db.mongo import movies_collection
from reaction_api.utils.reaction_initializer import default_reactions
from fastapi import HTTPException

class ReactionService:

    @staticmethod
    async def add_reaction(data):
        movie = await movies_collection.find_one({"_id": data.movie_id})

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        if "reactions" not in movie:
            await movies_collection.update_one(
                {"_id": data.movie_id},
                {"$set": {"reactions": default_reactions()}}
            )

        update_fields = {}

        if data.reaction:
            update_fields[f"reactions.emoji_reactions.{data.reaction}.count"] = 1

        if data.preference:
            update_fields[f"reactions.preferences.{data.preference}.count"] = 1

        if update_fields:
            await movies_collection.update_one(
                {"_id": data.movie_id},
                {"$inc": update_fields}
            )

        return {"message": "Reaction updated successfully"}
