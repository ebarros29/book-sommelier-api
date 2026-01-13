# Base image of Python 3.12
FROM python:3.12-slim

# Define environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installs system dependencies para MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only the Poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry
RUN poetry config virtualenvs.create false \
    && poetry lock \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the code
COPY . .

EXPOSE 8000

ENV FLASK_APP=api/main.py

# Command to run -> API
CMD ["sh", "-c", "alembic upgrade head && gunicorn --bind 0.0.0.0:8000 api.main:app"]