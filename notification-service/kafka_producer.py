from kafka import KafkaProducer
import json

producer = None

def get_producer():
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    return producer

def send_notification_sent(notification_id, order_id):
    # Šaljemo poruku na Kafka topic notification.sent
    get_producer().send('notification.sent', {
        'notification_id': notification_id,
        'order_id': order_id,
        'status': 'sent'
    })
    get_producer().flush()