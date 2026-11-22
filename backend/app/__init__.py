from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Who can call the API:
# - Angular dev server (ng serve) and any other localhost port
# - Electron loading the app from file:// (the browser sends Origin "null")
CORS_ORIGINS = [
    r"http://localhost(:\d+)?",
    r"http://127\.0\.0\.1(:\d+)?",
    "null",
]

# Load environment variables from the .env file
load_dotenv()

flask_key = os.getenv("FLASK_KEY")


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = flask_key
    # keep accents (Lácteos) readable in the JSON response
    app.json.ensure_ascii = False

    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

    # Error handler
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Endpoint not found"}, 404

    from .routes import products_bp

    app.register_blueprint(products_bp, url_prefix='/')

    return app
