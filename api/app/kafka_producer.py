import json
from kafka import KafkaProducer

KAFKA_SERVER = 'kafka_broker:9092'
TOPIC_NAME = 'indicators_topic'

def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def send_to_kafka(data_list: list[dict]):
    producer = get_producer()
    for item in data_list:
        producer.send(TOPIC_NAME, value=item)
    producer.flush()