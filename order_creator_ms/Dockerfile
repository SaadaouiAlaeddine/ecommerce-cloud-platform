# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

ENV PYTHONPATH=/app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python application into the container
COPY app /app

# Expose the port the app runs on
EXPOSE 80

# Run the application
CMD ["python", "main.py"]
