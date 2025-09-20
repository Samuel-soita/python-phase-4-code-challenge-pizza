from flask import Blueprint, jsonify
from sqlalchemy.orm import joinedload
from server.models import db, Restaurant, RestaurantPizza, Pizza

# ----------------------
# Blueprint Definition
# ----------------------
restaurants_bp = Blueprint("restaurants", __name__, url_prefix="/restaurants")


# ----------------------
# GET /restaurants
# ----------------------
@restaurants_bp.route("", methods=["GET"])
def get_restaurants():
    """Retrieve all restaurants (id, name, address)."""
    restaurants = Restaurant.query.all()
    data = [
        {
            "id": r.id,
            "name": r.name,
            "address": r.address,
        }
        for r in restaurants
    ]
    return jsonify(data), 200


# ----------------------
# GET /restaurants/<id>
# ----------------------
@restaurants_bp.route("/<int:id>", methods=["GET"])
def get_restaurant(id):
    """Retrieve a single restaurant and its pizzas."""
    
    # ----------------------
    # FIXED SQLAlchemy 2.x Issue:
    # Use class-bound attributes in joinedload instead of strings
    # ----------------------
    restaurant = (
        Restaurant.query.options(
            joinedload(Restaurant.restaurant_pizzas)  # load restaurant_pizzas
            .joinedload(RestaurantPizza.pizza)       # class-bound attribute instead of string
        )
        .filter_by(id=id)
        .first()
    )

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # ----------------------
    # Build response safely with nested pizzas
    # ----------------------
    data = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza_id": rp.pizza_id,
                "restaurant_id": rp.restaurant_id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients,
                } if rp.pizza else None,
            }
            for rp in restaurant.restaurant_pizzas
        ],
    }

    return jsonify(data), 200


# ----------------------
# DELETE /restaurants/<id>
# ----------------------
@restaurants_bp.route("/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    """Delete a restaurant by ID."""
    
    # ----------------------
    # FIXED: Use db.session.get() instead of deprecated query.get()
    # ----------------------
    restaurant = db.session.get(Restaurant, id)

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    try:
        db.session.delete(restaurant)
        db.session.commit()

        # ----------------------
        # FIXED: Return 204 No Content instead of 200 with JSON
        # ----------------------
        return "", 204

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete restaurant", "details": str(e)}), 500
