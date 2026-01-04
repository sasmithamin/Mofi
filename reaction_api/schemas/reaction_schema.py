from enum import Enum
from pydantic import BaseModel
from typing import Optional


class ReactionEnum(str, Enum):
    love = "😍"
    laugh = "😂"
    sad = "😢"
    angry = "😡"
    fire = "🔥"


class PreferenceEnum(str, Enum):
    like = "like"
    dislike = "dislike"


class ReactionCreate(BaseModel):
    user_id: str
    movie_id: str
    reaction: Optional[ReactionEnum] = None
    preference: Optional[PreferenceEnum] = None
