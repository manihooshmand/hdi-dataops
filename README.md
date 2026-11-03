# HDI Data Project

The project has two parts:
- **Pipeline** — `FastAPI` + `Kafka` + `PostgreSQL` + `Redis` ingests a World-Bank CSV, transforms wide→long, and serves it to a fact database.
- **Analysis notebook** — `notebooks/indicators_analysis.ipynb` explores the data with charts and a summary table across demographics, economy, health, labor, and education.


## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| API          | FastAPI, Uvicorn, Pandas            |
| Streaming    | Apache Kafka (KRaft mode)           |
| Databases    | PostgreSQL 15 (Staging & Fact)      |
| Cache        | Redis 7                             |
| Analysis     | Jupyter Notebook, Pandas, Matplotlib|
| Containerization | Docker, Docker Compose          |

---

## Project Structure

```
hdi-dataops/
├── api/                          # FastAPI ingestion service
│   ├── app/
│   │   ├── main.py               # /upload-csv endpoint
│   │   ├── ingestion.py          # wide -> long transform
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── database.py           # engine + session factory
│   │   ├── cache.py              # Redis cache helpers
│   │   └── kafka_producer.py     # Kafka producer
│   ├── Dockerfile
│   └── requirements.txt
│
├── consumer/                     # Kafka consumer service
│   ├── consumer.py               # reads Kafka -> fact DB
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   └── MiddleEastVsNordic.csv    # World Bank indicators (MEA, NOR, CHE)
│
├── notebooks/
│   └── indicators_analysis.ipynb # comparative analysis
│
└── docker-compose.yml            # 6 services: pg-staging, pg-fact, redis, kafka, api, consumer
```

---

## Quick Start

### 1. Run the pipeline

```bash
# Start all services in detached mode
docker-compose up --build -d

# Wait until all 6 services show 'Up (healthy)'
docker-compose ps
```

### 2. Upload the CSV

```bash
curl -X POST "http://localhost:8000/upload-csv/" \
     -F "file=@data/MiddleEastVsNordic.csv"
```

Expected response:
```json
{
  "status": "success",
  "message": "Processed 1425 rows. Sent 45998 records to Kafka.",
  "staging_rows": 1425,
  "kafka_records": 45998
}
```

### 3. Verify data

| Service        | Host port | Credentials                                |
|----------------|-----------|--------------------------------------------|
| Staging DB     | 5433      | user `staging_user`, pass `staging_pass`, db `staging_db` |
| Fact DB        | 5434      | user `fact_user`,   pass `fact_pass`,   db `fact_db`      |
| API            | 8000      | —                                          |
| Redis          | 6379      | pass `redis_pass`                          |
| Kafka          | 9092      | —                                          |

Logs:
```bash
docker-compose logs -f api
docker-compose logs -f consumer
```

### 4. Run the notebook

```bash
cd notebooks
jupyter lab indicators_analysis.ipynb
```

The notebook first tries the fact DB on `localhost:5434`. If Docker is not running, it automatically falls back to `../data/MiddleEastVsNordic.csv`, so the analysis works either way.

To execute it headless and save the outputs in place:
```bash
jupyter nbconvert --to notebook --execute notebooks/indicators_analysis.ipynb --inplace
```

---

## Notebook Contents

The notebook covers **9 indicators across 5 themes**, with charts and a summary table for the latest available year.

| Theme        | Indicator                                | Code                  |
|--------------|------------------------------------------|-----------------------|
| Demographics | Crude Birth Rate                         | `SP.DYN.CBRT.IN`      |
| Demographics | Life Expectancy at Birth                 | `SP.DYN.LE00.IN`      |
| Demographics | Total Fertility Rate                     | `SP.DYN.TFRT.IN`      |
| Economy      | GNI per Capita (Atlas method)            | `NY.GNP.PCAP.CD`      |
| Health       | Current Health Expenditure (% of GDP)    | `SH.XPD.CHEX.GD.ZS`   |
| Labor        | Unemployment, Total                      | `SL.UEM.TOTL.ZS`      |
| Labor        | Unemployment, Female                     | `SL.UEM.TOTL.FE.ZS`   |
| Labor        | Unemployment, Male                       | `SL.UEM.TOTL.MA.ZS`   |
| Education    | Tertiary School Enrollment               | `SE.TER.ENRR`         |

Charts are grouped into three multi-panel cells:
1. **Demographics** — birth rate, life expectancy, fertility
2. **Economy / Health / Education** — GNI, health expenditure, tertiary enrollment
3. **Labor** — unemployment (total, female, male)

A final summary table shows the latest available value for each indicator and country.

---

## Stop the Services

```bash
docker-compose down          # stop containers
docker-compose down -v       # also remove volumes (data wiped)
```

---

## Data Source

The CSV (`data/MiddleEastVsNordic.csv`) contains World Bank World Development Indicators for:
- **MEA** — Middle East, North Africa, Afghanistan & Pakistan (aggregate)
- **NOR** — Norway
- **CHE** — Switzerland

- **1,425 rows** (one per indicator × region)
- **65 year columns** (1960 – 2024)
- **426 unique indicators**
- After melt to long format: **45,998 records**
