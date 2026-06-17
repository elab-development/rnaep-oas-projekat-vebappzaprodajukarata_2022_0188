from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_notification_sent(notification_id, order_id):
    # Šaljemo poruku na Kafka topic notification.sent
    producer.send('notification.sent', {
        'notification_id': notification_id,
        'order_id': order_id,
        'status': 'sent'
    })
    producer.flush()