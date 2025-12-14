from pydantic import BaseModel

class RatingCreate(BaseModel):
    movie_id: str
    user_id: str
    stars: int
