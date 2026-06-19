from unittest.mock import patch, MagicMock


def make_fake_message(topic, value):
    msg = MagicMock()
    msg.topic = topic
    msg.value = value
    return msg


@patch('kafka_consumer.email_logs')
@patch('kafka_consumer.send_notification_sent')
@patch('kafka_consumer.send_ticket_email')
@patch('kafka_consumer.get_consumer')
def test_process_payment_completed(mock_get_consumer, mock_send_ticket, mock_send_notif, mock_email_logs):
    fake_message = make_fake_message('payment.completed', {
        'order_id': 1,
        'reservation_id': 10,
        'payment_id': 100,
        'user_email': 'test@example.com'
    })
    mock_get_consumer.return_value = [fake_message]

    from kafka_consumer import process_messages
    process_messages()

    mock_send_ticket.assert_called_once_with('test@example.com', 1, 10, 100)
    mock_email_logs.insert_one.assert_called_once()
    inserted_doc = mock_email_logs.insert_one.call_args[0][0]
    assert inserted_doc['type'] == 'ticket'
    assert inserted_doc['order_id'] == 1
    mock_send_notif.assert_called_once_with('notif_1', 1)


@patch('kafka_consumer.email_logs')
@patch('kafka_consumer.send_notification_sent')
@patch('kafka_consumer.send_error_email')
@patch('kafka_consumer.get_consumer')
def test_process_payment_failed(mock_get_consumer, mock_send_error, mock_send_notif, mock_email_logs):
    fake_message = make_fake_message('payment.failed', {
        'order_id': 2,
        'reservation_id': 20,
        'error': 'Insufficient funds',
        'user_email': 'test2@example.com'
    })
    mock_get_consumer.return_value = [fake_message]

    from kafka_consumer import process_messages
    process_messages()

    mock_send_error.assert_called_once_with('test2@example.com', 2, 'Insufficient funds')
    mock_email_logs.insert_one.assert_called_once()
    inserted_doc = mock_email_logs.insert_one.call_args[0][0]
    assert inserted_doc['type'] == 'error'
    mock_send_notif.assert_called_once_with('notif_2', 2)


@patch('kafka_consumer.email_logs')
@patch('kafka_consumer.send_notification_sent')
@patch('kafka_consumer.send_refund_email')
@patch('kafka_consumer.get_consumer')
def test_process_payment_refunded(mock_get_consumer, mock_send_refund, mock_send_notif, mock_email_logs):
    fake_message = make_fake_message('payment.refunded', {
        'refund_id': 30,
        'payment_id': 3,
        'amount': 500.0,
        'user_email': 'test3@example.com'
    })
    mock_get_consumer.return_value = [fake_message]

    from kafka_consumer import process_messages
    process_messages()

    mock_send_refund.assert_called_once_with('test3@example.com', 3, 30, 500.0)
    mock_email_logs.insert_one.assert_called_once()
    inserted_doc = mock_email_logs.insert_one.call_args[0][0]
    assert inserted_doc['type'] == 'refund'
    mock_send_notif.assert_called_once_with('notif_3', 3)