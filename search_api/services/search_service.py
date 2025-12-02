from search_api.db.mongo import movies_collection

class SearchService:
    @staticmethod
    async def search_movies(query: str):
        results = await movies_collection.find({
            "title": {"$regex": query, "$options": "i"}
        }).to_list(length=50)
        return results
    
