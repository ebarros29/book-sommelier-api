# Book Sommelier API

A simple public API built with **Python, Flask, and Web Scraping**.
The project extracts book data from *books.toscrape.com*, stores it locally, and exposes it via a REST API ready for **data science and machine learning use cases**.

---

## Project Goals

* Build a **web scraping pipeline** to collect book data
* Store data in a reusable format (CSV)
* Expose data through a **RESTful API (Flask)**
* Prepare the foundation for **future ML pipelines**

---

## Architecture Overview

```mermaid
flowchart LR
    A[Books to Scrape] --> B[Web Scraper]
    B --> C[CSV Dataset]
    C --> D[Flask API]
    D --> E[Consumers]
    E -->|DS / ML| F[ML Models]
```

**Pipeline:** Ingestion → Processing → API → Consumption

---

## 📂 Basic Project Structure

```text
.
├── api/
│   ├── routes.py        # API endpoints
│   └── main.py          # Flask app factory
│
├── scripts/
│   └── scraper.py       # Web scraping logic
│   └── insert_books.py  # Insert books on database logic
│
├── data/
│   └── books.csv        # Scraped dataset
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
# Clone repository
git clone git@github.com:ebarros29/book-sommelier-api.git
cd book-sommelier-api

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Run Web Scraping

```bash
python3 scripts/scraper.py
```

This will generate/update:

```
data/books.csv
```

---

## Run the API

```bash
docker-compose up -d
```

API will be available at:

```
http://localhost:8000
```

---

## API Endpoints

### Core Endpoints

| Method | Endpoint               | Description              |
| ------ | ---------------------- | ------------------------ |
| GET    | `/api/v1/books`        | List all books           |
| GET    | `/api/v1/books/<id>`   | Book details by ID       |
| GET    | `/api/v1/books/search` | Search by title/category |
| GET    | `/api/v1/categories`   | List categories          |
| GET    | `/api/v1/health`       | API health check         |

### Example

Interactive API documentation is available via Swagger UI. Open the docs in your browser after the server starts:

- Swagger UI: http://localhost:8000/docs
  - Also available on [/docs](./docs/)
- OpenAPI (JSON): http://localhost:8000/swagger.json

Use the Swagger UI to try requests like `GET /api/v1/books/search` with query parameters such as `category`, `title`, `min_rating`, and `max_price`.

---

## ML-Ready Vision

The API was designed to support future ML workflows:

* Feature extraction endpoints
* Training dataset generation
* Recommendation & prediction services

---

## 🌍 Deployment

TBD

---

## Tech Stack

* Python
* Flask
* Requests
