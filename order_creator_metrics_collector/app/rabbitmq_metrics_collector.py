import pika
import requests
import time
import argparse
import threading
from prometheus_client import start_http_server, Gauge

import pika
import requests
import time
import argparse
import threading
import os
from prometheus_client import start_http_server, Gauge

# Define Prometheus metrics
queue_message_count = Gauge('rabbitmq_queue_total_messages', 'Total messages in the queue', ['queue'])
exchange_message_rate_in = Gauge('rabbitmq_exchange_message_rate_in', 'Messages per second published to the exchange',
                                 ['exchange'])
exchange_message_rate_out = Gauge('rabbitmq_exchange_message_rate_out', 'Messages per second routed from the exchange',
                                  ['exchange'])

# Environment variables or default values for RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "my-rabbitmq.rabbitmq.svc.cluster.local")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_API_PORT = int(os.getenv("RABBITMQ_API_PORT", 15672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "adminpassword")


# Open a persistent connection and channel to RabbitMQ
def create_rabbitmq_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        )
    )
    channel = connection.channel()
    return connection, channel


# Initialize connection and channel globally
rabbitmq_connection, rabbitmq_channel = create_rabbitmq_connection()


# Function to get the message count for a queue
def get_queue_message_count(queue_name):
    try:
        queue = rabbitmq_channel.queue_declare(queue=queue_name, passive=True)
        message_count = queue.method.message_count
        queue_message_count.labels(queue=queue_name).set(message_count)
    except Exception as e:
        print(f"Error retrieving queue message count: {e}, with  queue name: {queue_name}")


# Function to get the message rate for an exchange
def get_exchange_message_rate(exchange_name):
    api_url = f"http://{RABBITMQ_HOST}:{RABBITMQ_API_PORT}/api/exchanges/%2F/{exchange_name}"
    try:
        response = requests.get(api_url, auth=(RABBITMQ_USER, RABBITMQ_PASS))
        response.raise_for_status()
        data = response.json()
        publish_in_rate = data.get("message_stats", {}).get("publish_in_details", {}).get("rate", 0)
        publish_out_rate = data.get("message_stats", {}).get("publish_out_details", {}).get("rate", 0)
        exchange_message_rate_in.labels(exchange=exchange_name).set(publish_in_rate)
        exchange_message_rate_out.labels(exchange=exchange_name).set(publish_out_rate)
    except Exception as e:
        print(f"Error retrieving exchange message rate: {e}")


# Function to update metrics at regular intervals
def update_metrics(target, target_type):
    while True:
        if target_type == "queue":
            get_queue_message_count(target)
        elif target_type == "exchange":
            get_exchange_message_rate(target)
        time.sleep(5)


# Main function to handle arguments and start the HTTP server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prometheus RabbitMQ Metrics Collector")
    parser.add_argument('--target', required=True, help="Queue or Exchange name")
    parser.add_argument('--type', required=True, choices=['queue', 'exchange'], help="Type: 'queue' or 'exchange'")
    parser.add_argument('--port', type=int, default=8000, help="Metrics port")
    args = parser.parse_args()

    # Start the Prometheus metrics server
    start_http_server(args.port)

    # Start the thread to update metrics
    threading.Thread(target=update_metrics, args=(args.target, args.type), daemon=True).start()

    # Keep the main thread alive
    while True:
        time.sleep(1)