from pydantic import BaseModel

class UploadResponse(BaseModel):
    status: str
    message: str
    staging_rows: int
    kafka_records: int