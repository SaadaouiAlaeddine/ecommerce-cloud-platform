FROM apache/spark:3.5.4 AS base

# Switch to root to install dependencies
USER root

# Add a group for GID 1001
RUN groupadd -g 1001 sparkgroup && \
    useradd -u 1001 -g sparkgroup sparkuser

# Set the working directory
WORKDIR /opt/spark/work-dir/

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the Python application into the container
COPY app/main.py .

# Set permissions for the sparkuser
RUN chown -R sparkuser:sparkgroup /opt/spark/work-dir

# Switch to the sparkuser
USER sparkuser

# Set the entrypoint
ENTRYPOINT ["spark-submit"]


