from kafka import KafkaProducer
from backend.app import app
from backend.encoder import JsonEncoder
import json


def send_message(topic, input_dict, partition=0):
    producer = KafkaProducer(bootstrap_servers=app.config['KAFKA_SERVER'],
                             value_serializer=lambda v: json.dumps(v, cls=JsonEncoder).encode('utf-8'))
    if partition > 0:
        future = producer.send(topic, input_dict, partition=partition)
    else:
        future = producer.send(topic, input_dict)
    try:
        future.get(timeout=app.config['KAFKA_TIME_OUT'])

    except Exception as e:
        app.logger.error(e, exc_info=True)
