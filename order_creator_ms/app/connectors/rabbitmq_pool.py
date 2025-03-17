import pika
import os
from queue import Queue
from threading import Lock

ORDER_EXCHANGE = os.getenv('RABBITMQ_ORDER_EXCHANGE', 'order-exchange')
EXCHANGE_TYPE = os.getenv('RABBITMQ_EXCHANGE_TYPE', 'direct')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', '172.19.0.101')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME', 'admin')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'adminpassword')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')


class RabbitMQConnection:
    def __init__(self):
        self.connection = None
        self.channel = None

    def get_connection(self):
        try:
            if not self.connection or self.connection.is_closed:
                print(f"Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT} with username {RABBITMQ_USERNAME}"
                      f" and password {RABBITMQ_PASSWORD} with exchange {ORDER_EXCHANGE}")
                credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    virtual_host=RABBITMQ_VHOST,
                    credentials=credentials
                ))
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange=ORDER_EXCHANGE, exchange_type=EXCHANGE_TYPE, durable=True)
            return self  # Return the RabbitMQConnection instance itself
        except Exception as e:
            print(f"Error while creating connection: {str(e)}")
            return None


class RabbitMQConnectionPool:
    def __init__(self, pool_size=5):
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)  # Connection pool using a queue
        self.lock = Lock()

        # Pre-fill the pool with RabbitMQ connections
        for _ in range(pool_size):
            self.pool.put(RabbitMQConnection())

    def get_instance_from_pool(self):
        """Get a RabbitMQ connection from the pool."""
        with self.lock:
            if not self.pool.empty():
                rabbitmq_connection = self.pool.get()  # Retrieve connection from the pool
                return rabbitmq_connection.get_connection()
            else:
                print("Connection pool is empty, creating a new connection.")
                # If the pool is empty, create a new connection
                return RabbitMQConnection().get_connection()

    def return_instance(self, rabbitmq_connection):
        """Return the connection to the pool."""
        with self.lock:
            if not self.pool.full():
                self.pool.put(rabbitmq_connection)
            else:
                print("Connection pool is full. Closing connection.")
                # Close the channel and the connection if the pool is full
                if rabbitmq_connection.channel:
                    rabbitmq_connection.channel.close()
                if rabbitmq_connection.connection:
                    rabbitmq_connection.connection.close()

    def publish_message(self, message, routing_key):
        rabbitmq_connection = self.get_instance_from_pool()
        if rabbitmq_connection and rabbitmq_connection.connection and rabbitmq_connection.channel:
            try:
                # Publish the message
                rabbitmq_connection.channel.basic_publish(
                    exchange=ORDER_EXCHANGE,
                    routing_key=routing_key,
                    body=message,  # Ensure message is serialized (e.g., JSON string)
                    properties=pika.BasicProperties(
                        delivery_mode=2  # Make message persistent
                    )
                )
                print(f"Published message {message} to {routing_key} queue")
            except pika.exceptions.AMQPConnectionError as e:
                print(f"RabbitMQ connection error: {str(e)}")
            except Exception as e:
                print(f"Error while publishing message: {str(e)}")
            finally:
                self.return_instance(rabbitmq_connection)  # Return connection to pool
