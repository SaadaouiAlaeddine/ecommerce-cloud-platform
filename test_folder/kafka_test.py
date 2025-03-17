from confluent_kafka import Consumer, KafkaException, KafkaError


def create_consumer():
    # Kafka configuration with SASL authentication
    conf = {
        'bootstrap.servers': '172.19.0.103:9094',  # Kafka server address
        'group.id': 'test-consumer-group',          # Consumer group ID
        'auto.offset.reset': 'earliest',            # Start reading from the earliest message
        'security.protocol': 'SASL_PLAINTEXT',     # Use SASL_PLAINTEXT protocol
        'sasl.mechanism': 'PLAIN',                  # Use PLAIN SASL mechanism
        'sasl.username': 'user1',                   # Your Kafka username
        'sasl.password': 'ODyCmWosJL',              # Your Kafka password
    }

    # Create and return the Kafka Consumer instance
    consumer = Consumer(conf)
    return consumer


def consume_messages(consumer, topic):
    # Subscribe to the Kafka topic
    consumer.subscribe([topic])

    # Poll for messages and consume them
    try:
        while True:
            msg = consumer.poll(timeout=1.0)  # 1 second timeout for polling
            if msg is None:
                continue  # No message received, keep polling
            if msg.error():
                # Handle error
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached {msg.partition}, offset {msg.offset()}")
                else:
                    raise KafkaException(msg.error())
            else:
                # Successfully received a message, print it
                print(f"Received message: {msg.value().decode('utf-8')}")

    except KeyboardInterrupt:
        print("Consumer interrupted")
    finally:
        # Close the consumer to clean up
        consumer.close()


def main():
    # Kafka topic to consume from
    topic = 'orders-topic'  # Replace with your Kafka topic name

    # Create a Kafka consumer
    consumer = create_consumer()

    # Consume messages from the specified topic
    consume_messages(consumer, topic)


if __name__ == "__main__":
    main()
