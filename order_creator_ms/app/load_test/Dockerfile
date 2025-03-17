# Use an official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /locust

# Install required dependencies
RUN pip install --no-cache-dir locust

# Expose Locust web UI and worker ports
EXPOSE 80 5557 5558

# Keep container running and use Locust with Prometheus
CMD ["locust"]