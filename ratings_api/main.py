from fastapi import FastAPI
from ratings_api.controllers.rating_controller import router

app = FastAPI(title="Ratings API")

app.include_router(router, tags=["Ratings"])

@app.get("/")
def health():
    return {"message": "Ratings API running"}
