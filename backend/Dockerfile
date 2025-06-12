FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root directory
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the wait-for-postgres script
COPY wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh

# Copy the backend application
COPY backend/ .

# Command to run the application
CMD ["/wait-for-postgres.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 