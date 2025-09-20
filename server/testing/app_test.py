import pytest
from faker import Faker
from server.app import create_app
from server.models import db, Restaurant, Pizza, RestaurantPizza


# -------------------- Fixtures -------------------- #
@pytest.fixture
def app():
    """Create a new app instance for each test with in-memory DB"""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client for the app"""
    return app.test_client()


fake = Faker()


# -------------------- Tests -------------------- #
def test_restaurants(app, client):
    """retrieves restaurants with GET request to /restaurants"""
    r1 = Restaurant(name=fake.name(), address=fake.address())
    r2 = Restaurant(name=fake.name(), address=fake.address())
    db.session.add_all([r1, r2])
    db.session.commit()

    response = client.get("/restaurants")
    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = response.get_json()
    restaurants = Restaurant.query.all()

    assert [r["id"] for r in data] == [r.id for r in restaurants]
    assert [r["name"] for r in data] == [r.name for r in restaurants]
    assert [r["address"] for r in data] == [r.address for r in restaurants]
    for r in data:
        assert "restaurant_pizzas" not in r


def test_restaurants_id(app, client):
    """retrieves one restaurant using its ID"""
    r = Restaurant(name=fake.name(), address=fake.address())
    db.session.add(r)
    db.session.commit()

    response = client.get(f"/restaurants/{r.id}")
    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = response.get_json()
    assert data["id"] == r.id
    assert data["name"] == r.name
    assert data["address"] == r.address
    assert "restaurant_pizzas" in data


def test_returns_404_if_no_restaurant_to_get(app, client):
    response = client.get("/restaurants/0")
    assert response.status_code == 404
    assert response.content_type == "application/json"
    assert response.get_json().get("error")


def test_deletes_restaurant_by_id(app, client):
    r = Restaurant(name=fake.name(), address=fake.address())
    db.session.add(r)
    db.session.commit()

    response = client.delete(f"/restaurants/{r.id}")
    assert response.status_code == 204

    assert Restaurant.query.filter_by(id=r.id).one_or_none() is None


def test_returns_404_if_no_restaurant_to_delete(app, client):
    response = client.delete("/restaurants/0")
    assert response.status_code == 404
    assert response.get_json().get("error") == "Restaurant not found"


def test_pizzas(app, client):
    p1 = Pizza(name=fake.name(), ingredients=fake.sentence())
    p2 = Pizza(name=fake.name(), ingredients=fake.sentence())
    db.session.add_all([p1, p2])
    db.session.commit()

    response = client.get("/pizzas")
    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = response.get_json()
    pizzas = Pizza.query.all()

    assert [p["id"] for p in data] == [p.id for p in pizzas]
    assert [p["name"] for p in data] == [p.name for p in pizzas]
    assert [p["ingredients"] for p in data] == [p.ingredients for p in pizzas]
    for p in data:
        assert "restaurant_pizzas" not in p


def test_creates_restaurant_pizzas(app, client):
    p = Pizza(name=fake.name(), ingredients=fake.sentence())
    r = Restaurant(name=fake.name(), address=fake.address())
    db.session.add_all([p, r])
    db.session.commit()

    response = client.post(
        "/restaurant_pizzas",
        json={"price": 3, "pizza_id": p.id, "restaurant_id": r.id}
    )
    assert response.status_code == 201
    assert response.content_type == "application/json"

    data = response.get_json()
    assert data["price"] == 3
    assert data["pizza_id"] == p.id
    assert data["restaurant_id"] == r.id
    assert data["id"]
    assert data["pizza"]
    assert data["restaurant"]

    rp = RestaurantPizza.query.filter_by(pizza_id=p.id, restaurant_id=r.id).first()
    assert rp.price == 3


def test_400_for_validation_error(app, client):
    p = Pizza(name=fake.name(), ingredients=fake.sentence())
    r = Restaurant(name=fake.name(), address=fake.address())
    db.session.add_all([p, r])
    db.session.commit()

    # price not in 1..30
    bad_prices = [0, 31]
    for price in bad_prices:
        response = client.post(
            "/restaurant_pizzas",
            json={"price": price, "pizza_id": p.id, "restaurant_id": r.id}
        )
        assert response.status_code == 400
        assert response.get_json()["errors"] == ["validation errors"]
