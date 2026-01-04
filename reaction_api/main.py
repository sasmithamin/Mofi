from fastapi import FastAPI
from reaction_api.controllers.reaction_controller import router

app = FastAPI(title="Reaction API")

app.include_router(router)
