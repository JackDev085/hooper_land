from models.attendance import Attendance
from models.games import Games
from models.games_schedules import GamesSchedules
from models.photos import Photos
from models.users import User, WorkoutLog
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
    
    # Migração tolerante a erros para adicionar colunas de streak se não existirem
    with engine.begin() as connection:
        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN streak_count INTEGER DEFAULT 0"))
        except Exception:
            pass
        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN last_workout_at VARCHAR"))
        except Exception:
            pass

def get_session():
    with Session(engine) as session:
        yield session