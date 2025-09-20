import pytest
from faker import Faker
from server.app import create_app   # ✅ import factory
from server.models import db, Restaurant, Pizza, RestaurantPizza

fake = Faker()

# Build a test app
app = create_app({
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # fast in-memory DB
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
})

class TestRestaurantPizza:
    '''Tests for RestaurantPizza model validation'''

    def setup_method(self, method):
        """Reset tables before each test for isolation."""
        with app.app_context():
            db.drop_all()
            db.create_all()

    def test_price_between_1_and_30(self):
        with app.app_context():
            pizza = Pizza(name=fake.name(), ingredients="Dough, Sauce, Cheese")
            restaurant = Restaurant(name=fake.name(), address="Main St")
            db.session.add_all([pizza, restaurant])
            db.session.commit()

            rp1 = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=1)
            rp2 = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=30)

            db.session.add_all([rp1, rp2])
            db.session.commit()

            assert rp1.price == 1
            assert rp2.price == 30

    def test_price_too_low(self):
        with app.app_context():
            pizza = Pizza(name=fake.name(), ingredients="Dough, Sauce, Cheese")
            restaurant = Restaurant(name=fake.name(), address="Main St")
            db.session.add_all([pizza, restaurant])
            db.session.commit()

            with pytest.raises(ValueError):
                bad_rp = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=0)
                db.session.add(bad_rp)
                db.session.commit()

    def test_price_too_high(self):
        with app.app_context():
            pizza = Pizza(name=fake.name(), ingredients="Dough, Sauce, Cheese")
            restaurant = Restaurant(name=fake.name(), address="Main St")
            db.session.add_all([pizza, restaurant])
            db.session.commit()

            with pytest.raises(ValueError):
                bad_rp = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=31)
                db.session.add(bad_rp)
                db.session.commit()
