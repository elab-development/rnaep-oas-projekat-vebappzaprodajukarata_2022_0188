from unittest.mock import patch, MagicMock


@patch('kafka_producer.get_producer')
def test_send_payment_completed_calls_producer(mock_get_producer):
    mock_instance = MagicMock()
    mock_get_producer.return_value = mock_instance

    from kafka_producer import send_payment_completed

    mock_payment = MagicMock()
    mock_payment.id = 1
    mock_payment.reservation_id = 10

    send_payment_completed(
        mock_payment, 
        "test@example.com",
        "Taylor Swift Concert",
        "2026-06-15T20:00:00",
        "Stark Arena",
        "Beograd")

    mock_instance.send.assert_called_once()
    args, kwargs = mock_instance.send.call_args
    assert args[0] == 'payment.completed'
    assert args[1]['order_id'] == 1
    assert args[1]['reservation_id'] == 10
    assert args[1]['user_email'] == "test@example.com"
    assert args[1]['event_name'] == "Taylor Swift Concert"
    assert args[1]['event_date'] == "2026-06-15T20:00:00"
    assert args[1]['venue_name'] == "Stark Arena"
    assert args[1]['venue_address'] == "Beograd"

@patch('kafka_producer.get_producer')
def test_send_payment_failed_calls_producer(mock_get_producer):
    mock_instance = MagicMock()
    mock_get_producer.return_value = mock_instance

    from kafka_producer import send_payment_failed

    mock_payment = MagicMock()
    mock_payment.id = 2
    mock_payment.reservation_id = 20

    send_payment_failed(mock_payment, "test@example.com", "Insufficient funds")

    mock_instance.send.assert_called_once()
    args, kwargs = mock_instance.send.call_args
    assert args[0] == 'payment.failed'
    assert args[1]['error'] == "Insufficient funds"