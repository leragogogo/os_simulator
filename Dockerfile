# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables:
# - Prevent Python from writing .pyc files
# - Force stdout/stderr to be unbuffered
# - Set matplotlib to use non-interactive backend for headless environments
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

# Upgrade pip and install build tools (optional but helps with some packages)
RUN pip install --upgrade pip && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the default command to run the simulator via CLI
ENTRYPOINT ["python", "cli.py"]
