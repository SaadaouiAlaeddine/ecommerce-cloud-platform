import json
import pika
from pymongo import MongoClient
from datetime import datetime


USERNAME = "mongo"
PASSWORD = "mongo"
HOST = "172.19.0.108"  # Example: localhost or mongo-service.mongodb.svc.cluster.local
PORT = "27017"  # Default MongoDB port
DATABASE = "ecommerce"
ORDER_COLLECTION = "orders"
ORDERS_QUEUE = "regular-orders"

# Connection URI
mongo_uri = f"mongodb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?authSource=admin"
client = MongoClient(mongo_uri)  # Change this if using a different host
db = client[DATABASE]
orders_collection = db[ORDER_COLLECTION]

def callback(ch, method, properties, body):
    order = json.loads(body.decode())
    print(f"Received order:", order)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    save_order(order)

def save_order(order):
    print(f"Saving order: {order}")
    insert_result = orders_collection.insert_one(order)
    print(f"Order inserted with ID: {insert_result.inserted_id}")

def main():
    print("Starting the microservice...")
    credentials = pika.PlainCredentials('admin', 'adminpassword')
    # Connection to RabbitMQ with the updated cluster name
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='172.19.0.101',
        virtual_host='/',
        credentials=credentials
    ))
    channel = connection.channel()

    # Start consuming messages
    channel.basic_consume(queue=ORDERS_QUEUE, on_message_callback=callback, auto_ack=False)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()

