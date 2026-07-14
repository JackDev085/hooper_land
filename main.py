from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from core.database import create_db_and_tables, engine

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from api.v1.endpoints.exercises import router as exercises_router
from api.v1.endpoints.workouts import router as workout_router
from api.v1.endpoints.auth import router as login_router
from api.v1.endpoints.health import router as health_router
from api.v1.endpoints.games import router as games_router
from api.v1.endpoints.games_days import router as games_days_router
from api.v1.endpoints.games_photos import router as games_photos_router
from api.v1.endpoints.groups import router as groups_router
from api.v1.endpoints.review import router as review_router
from api.v1.endpoints.notifications import router as notifications_router
from api.v1.endpoints.email import router as email_router
from api.v1.endpoints.dash import router as dash_router
from api.v1.endpoints.athlete_evolution import router as athlete_evolution_router

# Rate limiter: 60 requisições por minuto por IP (padrão global)
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables(engine)
    yield


app = FastAPI(lifespan= lifespan, title="Ballers085 backend" ,version="0.0.1")

# Registra o rate limiter no app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
      "*"    # dev frontend alt
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
app.include_router(groups_router)
app.include_router(review_router)
app.include_router(notifications_router)
app.include_router(email_router)
app.include_router(dash_router)
app.include_router(athlete_evolution_router)
