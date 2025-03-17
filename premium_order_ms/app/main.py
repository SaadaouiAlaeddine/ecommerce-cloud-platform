import json
import pika

def callback(ch, method, properties, body):
    order = json.loads(body.decode())
    print(f"Received order:", order)
    ch.basic_ack(delivery_tag=method.delivery_tag)

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
    channel.basic_consume(queue='priority-orders', on_message_callback=callback, auto_ack=False)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()