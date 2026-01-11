from fastapi import APIRouter, Form
from user_activities_api.services.activities_service import ActivitiesService

router = APIRouter(prefix="/activities", tags=["User Activities"])


# ---------- FAVORITES ----------

@router.post("/favorites")
async def add_favorite(
    user_id: str = Form(...),
    movie_id: str = Form(...)
):
    await ActivitiesService.add_favourite(user_id, movie_id)
    return {"message": "Movie added to favorites"}


@router.get("/favorites/{user_id}")
async def get_favorites(user_id: str):
    favorites = await ActivitiesService.get_favorites(user_id)
    return {"user_id": user_id, "favorites": favorites}


@router.delete("/favorites")
async def remove_favorite(
    user_id: str = Form(...),
    movie_id: str = Form(...)
):
    await ActivitiesService.remove_favorite(user_id, movie_id)
    return {"message": "Movie removed from favorites"}


# ---------- WATCHLIST ----------

@router.post("/watchlist")
async def add_watchlist(
    user_id: str = Form(...),
    movie_id: str = Form(...)
):
    await ActivitiesService.add_watchlist(user_id, movie_id)
    return {"message": "Movie added to watchlist"}


@router.get("/watchlist/{user_id}")
async def get_watchlist(user_id: str):
    watchlist = await ActivitiesService.get_watchlist(user_id)
    return {"user_id": user_id, "watchlist": watchlist}


@router.delete("/watchlist")
async def remove_watchlist(
    user_id: str = Form(...),
    movie_id: str = Form(...)
):
    await ActivitiesService.remove_watchlist(user_id, movie_id)
    return {"message": "Movie removed from watchlist"}
