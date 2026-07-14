from models.attendance import Attendance
from models.games import Games
from models.games_schedules import GamesSchedules
from models.photos import Photos
from models.users import User, WorkoutLog
from models.groups import Groups, GroupsAndUsers
from models.review import Reviews
from models.push_subscription import PushSubscriptions
from models.athlete_evolution import Competition, DailyJournal, GameStats, Goal
from models.exercises import Exercises
from models.workouts import Workouts
import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
import dotenv 


dotenv.load_dotenv()

PROD = os.getenv("PROD", "False")
DATABASE_URL = os.getenv("POSTGRES_URL_FASTAPI")

if PROD == "False" or not DATABASE_URL:
    # Use SQLite for development and testing
    engine = create_engine("sqlite:///./database.db", echo=True, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session