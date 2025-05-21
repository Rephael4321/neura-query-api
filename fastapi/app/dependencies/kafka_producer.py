from kafka import KafkaProducer
import json

_kafka_producer = None

def getKafkaProducer():
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = KafkaProducer(
                                bootstrap_servers="kafka:9092",
                                value_serializer = lambda v: json.dumps(v).encode("utf-8")
                                )
    return _kafka_producer
