import json
from flask import jsonify
from connectors.redis_connection import RedisConnection
from connectors.rabbitmq_pool import RabbitMQConnectionPool

redis_client = RedisConnection().get_client()
rabbitmq_pool = RabbitMQConnectionPool(pool_size=5)


def get_cached_order(order_id):
    order = redis_client.get(f"order:{order_id}")
    if order:
        return {"order": json.loads(order)}
    return {"error": "Order not found"}, 404

def cache_order(order, ttl=30):
    redis_client.setex(f"order:{order['order_id']}", ttl, json.dumps(order))
    print(f"Order {order['order_id']} cached for {ttl} seconds.")

def publish_orders(orders_list):
    try:
        for order in orders_list:
            cache_order(order, 30)
            rabbitmq_pool.publish_message(json.dumps(order), order['priority'])
        print(f"Published {len(orders_list)} orders to RabbitMQ.")
        return jsonify(
            {"message": f"{len(orders_list)} orders created and published, ", "orders": orders_list}), 201
    except Exception as e:
        return jsonify({"error": f"Error while creating orders: {str(e)}"}), 500