import hashlib
import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_staging_db, staging_engine, Base
from .models import StagingIndicator
from .schemas import UploadResponse
from .ingestion import transform_wide_to_long
from .kafka_producer import send_to_kafka
from .cache import get_cached_file, set_cached_file

app = FastAPI(title="Indicators Pipeline API")

# Create tables on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=staging_engine)

@app.post("/upload-csv/", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_staging_db)):
    # Read file content and generate hash for cache check
    contents = await file.read()
    file_hash = hashlib.md5(contents).hexdigest()
    
    # Return cached response if exists
    cached = get_cached_file(file_hash)
    if cached:
        return UploadResponse(**cached)
    
    try:
        # Read CSV, handle BOM if exists
        df = pd.read_csv(io.StringIO(contents.decode('utf-8-sig')))
        
        # 1. Load into Staging DB
        for _, row in df.iterrows():
            raw_json = row.drop(['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']).to_json()
            record = StagingIndicator(
                country_name=row['Country Name'],
                country_code=row['Country Code'],
                indicator_name=row['Indicator Name'],
                indicator_code=row['Indicator Code'],
                raw_data=raw_json
            )
            db.add(record)
        db.commit()
        
        # 2. Transform Wide to Long
        long_data = transform_wide_to_long(df)
        
        # 3. Publish to Kafka
        send_to_kafka(long_data)
        
        # Prepare response and cache it
        response_data = {
            "status": "success",
            "message": f"Processed {len(df)} rows. Sent {len(long_data)} records to Kafka.",
            "staging_rows": len(df),
            "kafka_records": len(long_data)
        }
        set_cached_file(file_hash, response_data)
        
        return UploadResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))