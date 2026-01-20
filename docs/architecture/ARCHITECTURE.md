## Architecture Documentation. 

This document presents the architecture for the Book Recommendation Data API project, concentrating on architectural choices, data flow from end-to-end, preparation for future scalability, and integration with Machine Learning models.  

## 1.🌐 Overview  
The Book Sommelier API is a Python-Flask based platform which includes:

1. Data collection through Web Scraping  
2. Use of book data in CSV files and a relational database  
3. REST API exposure for queries and analytical use cases  
4. Preparation for Machine Learning pipelines (recommendation systems, price analysis, NLP, etc.)  

The project runs a Pipeline → API → Consumption architecture, for incremental improvements and scaling.  

## 2. 🧩 Pipeline: Ingestion → Processing → API → Consumption

The Book Sommelier API pipeline verifies reliable data collection, normalization, storage and exposure for applications, analytics and machine learning projects. 

It consists of 4 sections that have well defined tasks, parts and architectural patterns. 

Here we break down each of the stages and how the data is flowing.  

This is where the full pipeline takes place.  

### 🎯 Ingestion Responsibilities
BookScraper runs a whole extraction workflow:  

#### Pagination Discovery
- Accesses the first catalog page (page-1.html). 
- Finds number of pages by HTML (ul.pager). 
- Holds last_page to control the scraping loop.

That allows for dynamic navigation as the site grows or scales its catalogue. 

#### Book URL Collection

For each page:
- Sends HTTP requests with proper headers (User-Agent). 
- Parses HTML using BeautifulSoup. 
- Extracts relative book links (href). 

The result is a _books_urls list with all the book pages on the site.  

#### Metadata Extraction 

For each individual book URL:
- Reads the detailed book page. 
- Extracts fields such as:
  a. Title.
  b. Raw price.
  c. Currency.
  d. Price in cents.
  e. Rating class.
  f. Category.
  g. Image URL.  

#### Data cleaning and standardization  
Before persistence:
- Currency conversion to international currency codes. 
- Normalization of price to integer cents. 
- Processing of optional fields (rating, image URL, category). 
- Basic validation and string cleaning (strip()).  

#### Persistence via DataStorage

The scraper is designed to be storage-agnostic through an external (DataStorage) interface. 
Currently, we use CSVWriter to persist structured data to: /data/books.csv. 
This CSV file becomes a dataset that downstream stages then consume.  

#### Technologies Used
1. Requests — HTTP calls to receive requests. 
2. BeautifulSoup — HTML parsing. 
3. Regex — price and currency normalization. 
4. Pandas (indirectly) — used later for CSV consumption.  

#### Output
📄 data/books.csv 

## 3. 🧬 Upcoming Scalability Architecture
The Book Sommelier API design was conceived to be adaptable now, and we built it up accordingly to take on new usage based on growing data volumes to be met as data set volumes grow and in turn Machine Learning applications are feeding the exposed data. 

The system is modular and any piece of it can be incrementally replaced or rearranged without having to rebuild/rebalance. 

Here are the primary scalability axes in the architectural design.  

### 3.1 Horizontal Scaling of the API
The API layer was set up to horizontally scale, so many instances are processed independently to absorb peak traffic. 

Docker-based packaging is used to facilitate this, so the application container can be replicated quickly across container-friendly platforms such as Render, Railway, Fly.io, or Kubernetes. 

With many instances running, a load balancer can evenly distribute requests ensuring:
- High availability. 
- Fault tolerance. 
- Improved performance. 
- Segregation of heavy workloads. 

It also supports independent workers to separate synchronous API requests from heavier processing in their background.  

### 3.2 Pipeline Scaling
As it stands, the pipeline is pretty straightforward: Scraping → CSV → Database import. 

This is fast for small/mild datasets, but becomes a bottleneck with new or higher volumes of data. 

A future evolution includes a distributed and highly scalable pipeline that includes Scraper → Queue (Kafka/RabbitMQ) → Parallel Processors → Database → API → ML. 

In this model:
- Scrapers send the messages to an asynchronous queue
- Each item is handled independently by a parallel consumer. 
- The database is continuously updated. 
- The API serves near real-time data.
- ML pipelines auto-receive fresh data.
  
Multiple scrapers, higher throughput and Big Data scale ingestion are possible with this design. 

### 3.3 Migration from CSV to Data Lake CSV 

It is great for prototyping, but it does not scale well when:
- High data volumes.
- Dataset versioning.
- Advanced analytical queries.
- Integration with large-scale ML pipelines.

The future migration will lead to more powerful formats and storage layers, such as:
- Parquet (columnar, compressed, optimized).
- ORC. Distributed storage solutions:
a. Amazon S3.
b. Google Cloud Storage.
c. MinIO (self-hosted S3 compatible).

This allows programs such as Apache Spark, AWS Glue, or Databricks to process datasets easily and back up advanced feature engineering cycles. 

### 3.4 Multi-Layer Caching

In order to prevent reprocessing commonly browsed queries (for example, top-rated books, categories and overview statistics) a caching layer like Redis can be added. 

Benefits include:
- Millisecond-level response times.
- Reduced database load.
- Cost-efficient scalability.
- Fast for dashboards and for repetitive consumers.

### 3.5 Observability and Monitoring

In an increasingly large scaled system, observability is an issue. 
The following are predicted, the architecture looks forward to the introduction of:
- Structured JSON logs (ELK stack, Datadog).
- Prometheus for metrics collection (latency, error rates, throughput).
- Grafana for dashboards and alerts.
- OpenTelemetry for distributed tracing of scrapers, API, database, and ML pipelines.

This allows for early detection of an anomaly as well as a clear view into the system's behavior. 

## 4. 🧠 Real-World Usage Scenarios for Data Science & ML

The architecture was designed as a solid foundation for Machine Learning pipelines, exposing clean, consistent, and standardized data. 

### 4.1 Price Regression

The API provides for predictions about the price of a book from many points of view like:
- Numerical ratings.
- Categories.
- Title tokens (TF-IDF, Bag-of-Words).
- Cover image features were extracted with CNN.

They can be utilized for using regression or boosting models to estimate predicted prices. 

### 4.2 Recommendation Systems

Based on category, title and metadata, the system facilitates recommendations via:
- Text similarity (cosine similarity).
- NLP embeddings (BERT, Sentence-BERT, Word2Vec).
- Category correlations.
- Collaborative methods, such as LightFM or matrix factorization.

It allows the creation of a genuine “Book Sommelier” experience. 

### 4.3 Market Analysis

The insights layer supports:
- Price comparison across categories.
- Rating distribution analysis.
- Identifying premium vs popular books.
- Temporal analysis of catalog evolution (future).

These results could be used for dashboards and exploratory analysis. 

### 4.4 Feature Store API

Its architecture anticipates future endpoints as: /api/v2/features/book/. 
These endpoints would expose precomputed feature vectors (e.g., title embeddings, one-hot categories and normalized prices) that can be directly consumed by the ML models and standardize the usage of feature vectors. 

## 5. 🤖 Machine Learning Integration Strategy

The architecture sets forth four maturity stages for integrating ML. 

### 5.1 Stage 1 — Data Preparation

A /ml directory consolidates datasets loaded via Pandas:
import pandas as pd. df = pd.read_csv("data/books.csv"). 

This initial stage consists of: 
Additional cleaning Feature generation Train/validation splits

### 5.2 Stage 2 — Model Training

Models recommended are: 
- RandomForest — good baseline for regression
- XGBoost / LightGBM — powerful performance for ranking and regression
- BERT / Sentence-BERT — semantic representation for titles
- LightFM — collaborative recommendation.

 ### 5.3 Stage 3 — Model Deployment using API
 
 It can also create endpoints like: 
 
 POST /api/v2/predictions/price 
 
 POST /api/v2/recommendations. 
 
 Models loaded in memory get features and return inference output. 
 
 ### 5.4 Stage 4 — MLOps
 
 For production readiness: 
 - Drift monitoring Model versioning Automated benchmarking
 - Data reprocessing Shared Feature Store.
 
 ## 6. 📦 Core System Components
 
 BookScraper — page collection and raw data extraction 
 
 CSVWriter — intermediate persistence layer 
 
 BookImportService — CSV ingestion, normalization, deduplication 
 
 BookRepository — database access abstraction via SQLAlchemy 
 
 Book Model — persisted entity 
 
 Books Blueprint — main public 
 
 API Insights Blueprint — analytical endpoints using Pandas 
 
 Dockerfile — application containerization docker-compose — local orchestration with API and Postgres 
 
 Alembic — database schema migrations. 
 
 ## 7. 📚 Tech and Architectural Decisions

The answer is Python, Flask with Blueprints, SQLAlchemy with PostgreSQL, Requests and BeautifulSoup for scraping, Pandas for analysis, Docker and docker-compose for infrastructure, and Alembic for migrations. 

CSV is a simple and efficient intermediate data source. 

## 8. 🧾 Conclusion

The Book Sommelier API architecture is modular, extensible, and fit for the future. 

It clearly separates scraping, processing, API, and analytics layers, and targets not just applications, but data teams as well. 

The design is very scalable, allows for new data sources, expanding features, and provides seamlessness between ML & MLOps workflows
