from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connections use docker service names
STAGING_DB_URL = "postgresql://staging_user:staging_pass@pg_staging:5432/staging_db"
FACT_DB_URL = "postgresql://fact_user:fact_pass@pg_fact:5432/fact_db"

staging_engine = create_engine(STAGING_DB_URL)
fact_engine = create_engine(FACT_DB_URL)

StagingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=staging_engine)
FactSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=fact_engine)

Base = declarative_base()

def get_staging_db():
    db = StagingSessionLocal()
    try:
        yield db
    finally:
        db.close()