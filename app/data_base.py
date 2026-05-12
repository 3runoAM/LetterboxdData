from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect
import os

data_base = SQLAlchemy()

def get_data_base_engine():
    return create_engine(os.getenv("DATABASE_URL"))

def is_missing_table():
    db_connection = get_data_base_engine()
    inspector = inspect(db_connection.engine)

    existing_tables = set(inspector.get_table_names())
    required_tables = {"diary", "ratings", "watched", "watched_enriched"}

    return False if len(required_tables - existing_tables) == 0 else True
