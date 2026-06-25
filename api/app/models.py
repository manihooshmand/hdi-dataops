from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base

class StagingIndicator(Base):
    __tablename__ = "staging_indicators"
    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String)
    country_code = Column(String, index=True)
    indicator_name = Column(String)
    indicator_code = Column(String, index=True)
    raw_data = Column(Text) # Years stored as JSON string

class FactIndicator(Base):
    __tablename__ = "fact_indicators"
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String, index=True)
    indicator_code = Column(String, index=True)
    year = Column(Integer, index=True)
    value = Column(Float, nullable=True)