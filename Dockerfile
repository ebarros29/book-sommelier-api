# Base image of Python 3.12
FROM python:3.12-slim

# Define environment variables to avoid .pyc files and log buffers.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Defines the working directory.
WORKDIR /app

# Installs system dependencies.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only the Poetry configuration files first (improves Docker caching).
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to install dependencies in the global Python container.
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the code to the container.
COPY . .

# Expose the port (Flask uses 5000 by default, but you can keep it at 8000 if you prefer).
EXPOSE 8000

# Environment variable for Flask
ENV FLASK_APP=api/main.py

# Command to run: Scraper -> Loader -> API
CMD ["sh", "-c", "python scripts/scraper.py && python scripts/loader.py && gunicorn --bind 0.0.0.0:8000 api.main:app"]