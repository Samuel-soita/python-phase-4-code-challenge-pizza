from flask import Blueprint, jsonify
from server.models import Pizza

pizzas_bp = Blueprint("pizzas", __name__, url_prefix="/pizzas")

# GET /pizzas
@pizzas_bp.route("/", methods=["GET"], strict_slashes=False)
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([p.to_dict(only=("id", "name", "ingredients")) for p in pizzas]), 200
