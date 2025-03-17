# Use a lightweight Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and other necessary files into the container
COPY rabbitmq_metrics.py /app/rabbitmq_metrics.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the application will run on
EXPOSE 8000

# Command to run the Python script
CMD ["python", "/app/rabbitmq_metrics_collector.py"]
