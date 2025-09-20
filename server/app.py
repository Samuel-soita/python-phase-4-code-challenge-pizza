#!/usr/bin/env python3
import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_restful import Api

# Import models and db
from server.models import db, Restaurant, RestaurantPizza, Pizza

# Import blueprints
from server.routes.restaurants import restaurants_bp
from server.routes.pizzas import pizzas_bp
from server.routes.restaurant_pizzas import restaurant_pizzas_bp

# Initialize extensions globally
migrate = Migrate()
api = Api()


def create_app(test_config=None):
    """Factory to create and configure the Flask app."""
    app = Flask(__name__)

    # ---------------- Database Config ---------------- #
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.environ.get(
        "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )
    app.config.update(
        SQLALCHEMY_DATABASE_URI=DATABASE,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_COMPACT=False,
    )

    if test_config:
        app.config.update(test_config)

    # ---------------- Initialize Extensions ---------------- #
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)  # Optional (only if you’ll use Flask-RESTful)

    # ---------------- Register Blueprints ---------------- #
    app.register_blueprint(restaurants_bp)
    app.register_blueprint(pizzas_bp)
    app.register_blueprint(restaurant_pizzas_bp)

    # ---------------- Error Handlers ---------------- #
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    # ---------------- Root Route ---------------- #
    @app.route("/")
    def index():
        return "<h1>🍕 Pizza Restaurants API - Phase 4 Challenge</h1>"

    return app


# ---------------- Entry Point ---------------- #
if __name__ == "__main__":
    app = create_app()
    app.run(port=5555, debug=True)
