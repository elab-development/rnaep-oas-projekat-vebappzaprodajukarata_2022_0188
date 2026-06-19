from kafka import KafkaConsumer
from database import email_logs
from kafka_producer import send_notification_sent
from postmark_client import send_ticket_email, send_error_email, send_refund_email
import json
from datetime import datetime, UTC

consumer = None

def get_consumer():
    # Kreira KafkaConsumer SAMO kada je prvi put potreban,
    # ne odmah pri uvozu ovog fajla (sprečava timeout u testovima)
    global consumer
    if consumer is None:
        consumer = KafkaConsumer(
            'payment.completed',
            'payment.failed',
            'payment.refunded',
            bootstrap_servers='kafka:9092',
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id='notification-group',
            auto_offset_reset='earliest'
        )

def process_messages():
    for message in get_consumer():
        topic = message.topic
        data = message.value

        if topic == 'payment.completed':
            notification_id = f"notif_{data['order_id']}"
            
            # Šaljemo email sa ulaznicom
            send_ticket_email(
                data['user_email'],
                data['order_id'],
                data['reservation_id'],
                data['payment_id']
            )
            
            # Kreiramo email log u MongoDB
            email_logs.insert_one({
                'notification_id': notification_id,
                'order_id': data['order_id'],
                'user_email': data['user_email'],
                'type': 'ticket',
                'email_body': {
                    'order_id': data['order_id'],
                    'reservation_id': data['reservation_id'],
                    'payment_id': data['payment_id']
                },
                'status': 'sent',
                'sent_at': datetime.now(UTC),
                'created_at': datetime.now(UTC)
            })
            
            # Šaljemo poruku na notification.sent topic
            send_notification_sent(notification_id, data['order_id'])
            print(f"Ticket email sent for order {data['order_id']}")

        elif topic == 'payment.failed':
            notification_id = f"notif_{data['order_id']}"
            
            # Šaljemo email o grešci
            send_error_email(
                data['user_email'],
                data['order_id'],
                data['error']
            )
            
            # Kreiramo email log u MongoDB
            email_logs.insert_one({
                'notification_id': notification_id,
                'order_id': data['order_id'],
                'user_email': data['user_email'],
                'type': 'error',
                'email_body': {
                    'error_message': data['error'],
                    'order_id': data['order_id']
                },
                'status': 'sent',
                'sent_at': datetime.now(UTC),
                'created_at': datetime.now(UTC)
            })
            
            # Šaljemo poruku na notification.sent topic
            send_notification_sent(notification_id, data['order_id'])
            print(f"Error email sent for order {data['order_id']}")

        elif topic == 'payment.refunded':
            notification_id = f"notif_{data['payment_id']}"
            
            # Šaljemo email o refundaciji
            send_refund_email(
                data['user_email'],
                data['payment_id'],
                data['refund_id'],
                data['amount']
            )
            
            # Kreiramo email log u MongoDB
            email_logs.insert_one({
                'notification_id': notification_id,
                'order_id': data['payment_id'],
                'user_email': data['user_email'],
                'type': 'refund',
                'email_body': {
                    'refund_id': data['refund_id'],
                    'payment_id': data['payment_id'],
                    'amount': data['amount']
                },
                'status': 'sent',
                'sent_at': datetime.now(UTC),
                'created_at': datetime.now(UTC)
            })
            
            # Šaljemo poruku na notification.sent topic
            send_notification_sent(notification_id, data['payment_id'])
            print(f"Refund email sent for payment {data['payment_id']}")