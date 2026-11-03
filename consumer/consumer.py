import json
from kafka import KafkaConsumer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import shared models structure (or redefine if strictly decoupled)
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class FactIndicator(Base):
    __tablename__ = "fact_indicators"
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String, index=True)
    indicator_code = Column(String, index=True)
    year = Column(Integer, index=True)
    value = Column(Float, nullable=True)

# DB Setup
FACT_DB_URL = "postgresql://fact_user:fact_pass@pg_fact:5432/fact_db"
engine = create_engine(FACT_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create fact table
Base.metadata.create_all(bind=engine)

# Kafka Setup
KAFKA_SERVER = 'kafka_broker:9092'
TOPIC_NAME = 'indicators_topic'

def consume():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='earliest',
        group_id='fact_group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Consumer started. Listening...")
    db = SessionLocal()
    
    try:
        for message in consumer:
            data = message.value
            record = FactIndicator(
                country_code=data['country_code'],
                indicator_code=data['indicator_code'],
                year=int(data['year']),
                value=float(data['value'])
            )
            db.add(record)
            db.commit()
            print(f"Inserted: {data['country_code']} | {data['indicator_code']} | {data['year']}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    consume()