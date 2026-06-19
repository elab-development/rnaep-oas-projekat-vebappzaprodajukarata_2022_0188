from kafka import KafkaProducer
import json

producer = None

def get_producer():
    # Kreira KafkaProducer SAMO kada je prvi put potreban,
    # ne odmah pri uvozu ovog fajla (sprečava timeout u testovima)
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    return producer

def send_payment_completed(payment, user_email):
# Šaljemo poruku kada je plaćanje uspješno

    get_producer().send('payment.completed', {
        'order_id': payment.id,
        'reservation_id': payment.reservation_id,
        'payment_id': payment.id,
        'user_email': user_email
    })
    get_producer().flush()

def send_payment_failed(payment, user_email, error):
# Šaljemo poruku kada plaćanje nije uspjelo

    get_producer().send('payment.failed', {
        'order_id': payment.id,
        'reservation_id': payment.reservation_id,
        'error': error,
        'user_email': user_email
    })
    get_producer().flush()

def send_payment_refunded(refund, user_email):
# Šaljemo poruku kada je refundacija uspješna

    get_producer().send('payment.refunded', {
        'refund_id': refund.id,
        'payment_id': refund.payment_id,
        'amount': refund.amount,
        'user_email': user_email
    })
    get_producer().flush()