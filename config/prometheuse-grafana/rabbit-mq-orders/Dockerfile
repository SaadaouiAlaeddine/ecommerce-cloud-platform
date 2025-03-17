# Use a base Python image
FROM python:3.9-slim

# Install required dependencies
RUN pip install pika requests prometheus_client

# Create a directory for the script (this is where Kubernetes will mount the ConfigMap)
WORKDIR /app

# Define the command to run the script (the script will be mounted from the ConfigMap)
CMD ["python", "/app/rabbitmq_metrics_collector.py"]

