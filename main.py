from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import create_db_and_tables, engine

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints.exercises import router as exercises_router
from api.v1.endpoints.workouts import router as workout_router
from api.v1.endpoints.auth import router as login_router
from api.v1.endpoints.health import router as health_router
from api.v1.endpoints.games import router as games_router
from api.v1.endpoints.games_days import router as games_days_router
from api.v1.endpoints.games_photos import router as games_photos_router


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables(engine)
    yield


app = FastAPI(lifespan= lifespan, title="Ballers085 backend" ,version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ballers085.vercel.app",
        "http://localhost:5173",       # dev frontend
        "http://127.0.0.1:5173",       # dev frontend alt
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")
app.include_router(login_router)
app.include_router(workout_router)
app.include_router(exercises_router)
app.include_router(health_router)
app.include_router(games_days_router)
app.include_router(games_photos_router)
app.include_router(games_router)
