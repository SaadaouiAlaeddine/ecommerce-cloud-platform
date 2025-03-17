from flask import jsonify

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

def get_products_by_category(category):
    if category not in PRODUCT_CATEGORY_MAPPING:
        return jsonify({"error": "Invalid category"}), 400

    return jsonify({"products": PRODUCT_CATEGORY_MAPPING[category]})

def get_all_categories():
    return jsonify({"categories": list(PRODUCT_CATEGORY_MAPPING.keys())})

def get_all_products():
    all_products = []
    for products in PRODUCT_CATEGORY_MAPPING.values():
        all_products.extend(products)
    return jsonify({"products": all_products})

def get_all_products_by_category():
    all_products_by_category = {}
    for category, products in PRODUCT_CATEGORY_MAPPING.items():
        all_products_by_category[category] = products
    return jsonify(all_products_by_category)