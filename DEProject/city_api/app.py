import os
from pathlib import Path
from flask import Flask, jsonify
from dotenv import load_dotenv

from .database import initialize_database
from .routes import cities_bp


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    default_database = Path(__file__).with_name("cities.db")
    app.config.from_mapping(
        DATABASE=os.environ.get(
            "CITY_API_DATABASE_URL",
            os.environ.get("CITY_API_DATABASE", str(default_database)),
        )
    )
    if test_config:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE"])
    app.register_blueprint(cities_bp)

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found."}), 404

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
