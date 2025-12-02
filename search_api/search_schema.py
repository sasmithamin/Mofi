from pydantic import BaseModel

class SearchResult(BaseModel):
    title: str
    description: str =None
    movie_id: str

    