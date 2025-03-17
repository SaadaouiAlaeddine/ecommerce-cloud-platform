from flask import Blueprint
import models.product_category as product_category
stock_controller = Blueprint('stock_controller', __name__)

@stock_controller.route('/', methods=['GET'])
def hello():
    return "Hello", 200

@stock_controller.route('/stock/<category_name>', methods=['GET'])
def get_products_by_category(category_name):
    return product_category.get_products_by_category(category_name)

@stock_controller.route('/stock/all-categories', methods=['GET'])
def get_all_categories():
    return product_category.get_all_categories()

@stock_controller.route('/stock/all-products-by-category', methods=['GET'])
def get_all_products_by_category():
    return product_category.get_all_products_by_category()

@stock_controller.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy"}