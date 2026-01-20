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

## Authentication (Admin)

The project includes simple JWT-based authentication to protect admin routes (scraping/import). Credentials and secrets are configured via environment variables.

- Admin credentials (defaults):
  - `ADMIN_USERNAME` (default: `admin`)
  - `ADMIN_PASSWORD` (default: `password`)
- JWT secret: `JWT_SECRET_KEY` (default: generated fallback in app)

### Endpoints

| Method | Endpoint                         | Description |
| ------ | -------------------------------- | ----------- |
| POST   | `/api/v1/auth/login`             | Obtain `access_token` and `refresh_token` by posting JSON `{ "username": "...", "password": "..." }` |
| POST   | `/api/v1/auth/refresh`           | Exchange a `refresh_token` for a new `access_token` by posting JSON `{ "refresh_token": "..." }` |

Protected admin routes (require `Authorization: Bearer <access_token>`):

| Method | Endpoint                        | Description |
| ------ | ------------------------------- | ----------- |
| POST   | `/api/v1/scraping/trigger`      | Start scraping (background) |
| POST   | `/api/v1/scraping/import`       | Import CSV into DB (background) |
| GET    | `/api/v1/scraping/trigger/status` | Scraping status |
| GET    | `/api/v1/scraping/import/status`  | Import status |

### Examples

1) Login to obtain tokens:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"password"}'

# Response: {"access_token":"...","refresh_token":"..."}
```

2) Use access token to trigger import:

```bash
curl -X POST http://localhost:8000/api/v1/scraping/import \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

3) Refresh access token:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"<REFRESH_TOKEN>"}'

# Response: {"access_token":"..."}
```

Note: This is a minimal auth implementation intended for development. For production, replace with a proper user store, secure secrets management, HTTPS, and token revocation.

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
