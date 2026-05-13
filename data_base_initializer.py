from app.data_base import data_base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from app.models import Movie, Genre, Director, WatchLog

load_dotenv()

def initialize():
    try:
        engine = create_engine(os.getenv("DATABASE_URL"))
        data_base.metadata.create_all(engine)
    except Exception as e:
        print(f"ERROR: Couldn't create tables\n>> {e}")


if __name__ == "__main__":
    initialize()