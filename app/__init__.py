from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

flask_key = os.getenv("FLASK_KEY")


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = flask_key

    return app
