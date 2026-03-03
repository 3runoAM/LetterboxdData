import os
from flask import Flask
from dotenv import load_dotenv  # Importa a biblioteca

# Carrega as variáveis que estão dentro do arquivo .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    from .routes import main
    app.register_blueprint(main)

    return app