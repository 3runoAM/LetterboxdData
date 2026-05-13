import os

from .data_base import data_base
from .routes import main
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

    data_base.init_app(app)

    app.register_blueprint(main)

    return app