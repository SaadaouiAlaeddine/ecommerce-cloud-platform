from flask import Blueprint, request, jsonify
import services.order_service as order_service
import services.stock_service as stock_service
from models.order import Order
from validators.jwt_validator import validate_jwt
import logging

order_controller = Blueprint('order_controller', __name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
@order_controller.route('/', methods=['GET'])
@validate_jwt
def hello():
    return "Hello", 200

@order_controller.route('/order/<order_id>', methods=['GET'])
@validate_jwt
def get_cached_order(order_id):
    return order_service.get_cached_order(order_id)

@order_controller.route('/create', methods=['POST'])
@validate_jwt
def create_orders():
    try:
        data = request.get_json()
        number_of_orders = data.get('number_of_orders', 1)
        if not isinstance(number_of_orders, int) or number_of_orders <= 0:
            return jsonify({"error": "Invalid numberOfOrder"}), 400
        orders_list = Order.create_json_order(number_of_orders)
        return order_service.publish_orders(orders_list)
    except Exception as e:
        return jsonify({"error": f"Error while creating orders: {str(e)}"}), 500

@order_controller.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy app"}

@order_controller.route('/all-products-by-category', methods=['GET'])
def get_all_products_by_category():
    all_products = stock_service.get_all_products_by_category()
    logger.info(f"Getting all products by category: {all_products}")
    return all_products