#!/usr/bin/env python3

from server.app import create_app
from server.models import db, Restaurant, Pizza, RestaurantPizza

app = create_app()

def seed_data():
    with app.app_context():
        try:
            print("🔄 Clearing old data...")
            # Delete in the correct order due to foreign key constraints
            db.session.query(RestaurantPizza).delete()
            db.session.query(Pizza).delete()
            db.session.query(Restaurant).delete()
            db.session.commit()
            print("🗑️ Old data cleared successfully.")

            # Create restaurants
            print("🍽️ Creating restaurants...")
            restaurants = [
                Restaurant(name="Karen's Pizza Shack", address="123 Main St"),
                Restaurant(name="Sanjay's Pizza", address="456 Oak Ave"),
                Restaurant(name="Kiki's Pizza", address="789 Pine Rd"),
            ]
            db.session.add_all(restaurants)
            db.session.commit()
            print(f"✅ {len(restaurants)} restaurants created.")

            # Create pizzas
            print("🍕 Creating pizzas...")
            pizzas = [
                Pizza(name="Emma", ingredients="Dough, Tomato Sauce, Cheese"),
                Pizza(name="Geri", ingredients="Dough, Tomato Sauce, Cheese, Pepperoni"),
                Pizza(name="Melanie", ingredients="Dough, Sauce, Ricotta, Red Peppers, Mustard"),
            ]
            db.session.add_all(pizzas)
            db.session.commit()
            print(f"✅ {len(pizzas)} pizzas created.")

            # Link restaurants and pizzas using relationships (safe way)
            print("📦 Linking restaurants and pizzas with prices...")
            restaurants[0].restaurant_pizzas.append(RestaurantPizza(pizza=pizzas[0], price=10))
            restaurants[1].restaurant_pizzas.append(RestaurantPizza(pizza=pizzas[1], price=12))
            restaurants[2].restaurant_pizzas.append(RestaurantPizza(pizza=pizzas[2], price=15))
            db.session.commit()
            print("✅ Restaurant-pizza links created successfully.")

            print("🎉 Database seeding completed successfully!")

        except Exception as e:
            db.session.rollback()
            print("❌ Error during seeding:", e)


if __name__ == "__main__":
    seed_data()
