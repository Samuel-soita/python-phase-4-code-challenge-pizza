from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)

    # Relationship: One Restaurant has many RestaurantPizzas
    restaurant_pizzas = relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    # Serializer rules: avoid recursion
    serialize_rules = ("-restaurant_pizzas.restaurant",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(String)

    # Relationship: One Pizza has many RestaurantPizzas
    restaurant_pizzas = relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan"
    )

    serialize_rules = ("-restaurant_pizzas.pizza",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    pizza_id = Column(Integer, ForeignKey("pizzas.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)

    # Relationships
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")

    serialize_rules = ("restaurant", "pizza")

    # Validation
    @validates("price")
    def validate_price(self, key, value):
        if not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
