# HDI Pipeline

A lightweight end-to-end data engineering pipeline using FastAPI, Kafka, PostgreSQL, and Redis.

## Architecture Flow
CSV Upload -> FastAPI (Staging DB) -> Pandas Melt (Wide to Long) -> Kafka -> Consumer (Fact DB)

## Tech Stack
- **API:** FastAPI, Python
- **Databases:** PostgreSQL (Staging & Fact)
- **Containerization:** Docker
- **Cache:** Redis
- **Streaming:** Apache Kafka

## Quick Start

1. **Run the infrastructure and services:**
```bash
docker-compose up --build -d
```

2. **Check health status:**
```bash
docker-compose ps
# Wait until all 6 services show 'Up (healthy)'
```

3. **Upload the CSV file:**
```bash
curl -X POST "http://localhost:8000/upload-csv/" -F "file=@data/MiddleEastVsNordic.csv"
```

## Verify Data

- **Staging DB:** `localhost:5433` (user: `staging_user`, pass: `staging_pass`, db: `staging_db`)
- **Fact DB:** `localhost:5434` (user: `fact_user`, pass: `fact_pass`, db: `fact_db`)
- **API Logs:** `docker-compose logs api`
- **Consumer Logs:** `docker-compose logs -f consumer`

## Stop Services
```bash
docker-compose down
```