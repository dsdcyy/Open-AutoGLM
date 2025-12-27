# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (ADB is required)
RUN apt-get update && apt-get install -y \
    adb \
    android-tools-adb \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/

# Expose the port the app runs on
ENV PORT=8001
EXPOSE $PORT

# Command to run the application
# We use host 0.0.0.0 to make it accessible outside container
CMD ["sh", "-c", "python web_ui/main.py --port $PORT"]
