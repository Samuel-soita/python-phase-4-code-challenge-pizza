from flask import Blueprint, request, jsonify
from server.models import db, RestaurantPizza, Restaurant, Pizza

# Blueprint definition
restaurant_pizzas_bp = Blueprint("restaurant_pizzas", __name__, url_prefix="/restaurant_pizzas")

# POST /restaurant_pizzas
@restaurant_pizzas_bp.route("/", methods=["POST"], strict_slashes=False)
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # --------------------------
    # Standardized validation
    # --------------------------
    if price is None or pizza_id is None or restaurant_id is None:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        price = int(price)
        if price < 1 or price > 30:
            return jsonify({"errors": ["validation errors"]}), 400  # matches test
    except (ValueError, TypeError):
        return jsonify({"errors": ["validation errors"]}), 400

    # Check if pizza and restaurant exist
    pizza = db.session.get(Pizza, pizza_id)       # SQLAlchemy 2.x style
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not pizza or not restaurant:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(rp)
        db.session.commit()

        return jsonify(
            rp.to_dict(
                only=(
                    "id",
                    "price",
                    "pizza_id",
                    "restaurant_id",
                    "pizza.id",
                    "pizza.name",
                    "pizza.ingredients",
                    "restaurant.id",
                    "restaurant.name",
                    "restaurant.address",
                )
            )
        ), 201

    except Exception:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400
