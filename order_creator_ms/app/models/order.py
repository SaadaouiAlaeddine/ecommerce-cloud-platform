from faker import Faker
import random

fake = Faker()
PRODUCT_CATEGORY_MAPPING = {
    "Electronics": ["Laptop", "Smartphone", "Headphones", "Smartwatch", "Tablet"],
    "Home & Kitchen": ["Blender", "Microwave", "Coffee Maker", "Toaster", "Vacuum Cleaner"],
    "Toys": ["Toy Car", "Doll", "Lego Set", "Action Figure", "Puzzle"],
    "Sports": ["Tennis Racket", "Football", "Basketball", "Yoga Mat", "Jump Rope"],
    "Health & Beauty": ["Shampoo", "Face Cream", "Toothpaste", "Hair Dryer", "Sunscreen"],
    "Books": ["Novel", "Biography", "Cookbook", "Science Fiction", "Textbook"],
    "Clothing": ["T-Shirt", "Jeans", "Sweater", "Jacket", "Sneakers"],
    "Automotive": ["Car Battery", "Tire", "Car Wax", "Oil Filter", "Brake Pads"]
}

PRIORITY_TYPES = ["priority", "regular"]

class Order:
    def __init__(self, order_id=None, customer=None, product=None, priority=None):
        if order_id is None:
            order_id = fake.uuid4()  # Generate a unique order ID

        if customer is None:
            customer = {
                "name": fake.name(),
                "email": fake.email(),
                "address": fake.address()
            }

        if product is None:
            category = random.choice(list(PRODUCT_CATEGORY_MAPPING.keys()))
            name = random.choice(PRODUCT_CATEGORY_MAPPING[category])
            product = {
                "name": name,
                "category": category,
                "price": round(random.uniform(10, 500), 2)
            }

        if priority is None:
            priority = random.choice(PRIORITY_TYPES)

        self.priority = random.choice(PRIORITY_TYPES)
        self.order_id = order_id
        self.customer = customer
        self.product = product
        self.priority = priority

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer": self.customer,
            "product": self.product,
            "priority": self.priority }

    @staticmethod
    def create_json_order(number_of_orders=0):
        orders = []
        for _ in range(number_of_orders):
            order = Order()
            orders.append(order.to_dict())
        return orders