from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect
import os

data_base = SQLAlchemy()

def get_data_base_engine():
    return create_engine(os.getenv("DATABASE_URL"))
