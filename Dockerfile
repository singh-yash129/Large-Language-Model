# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only requirements.txt first to leverage Docker cache for dependencies
COPY requirements.txt .

# Upgrade pip and install dependencies in one step to save space and time
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install additional system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    npm \
    git \
    sqlite3 \
    pandoc \
    imagemagick \
    && npm install -g prettier@3.4.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . .

# Expose port 8000 to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "app.py"]
