from flask import Flask
from .db import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .routes.restaurants import restaurants_bp
    from .routes.pizzas import pizzas_bp
    from .routes.restaurant_pizzas import restaurant_pizzas_bp

    app.register_blueprint(restaurants_bp)
    app.register_blueprint(pizzas_bp)
    app.register_blueprint(restaurant_pizzas_bp)

    return app
