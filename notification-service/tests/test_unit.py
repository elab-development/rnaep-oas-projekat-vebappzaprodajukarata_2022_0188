from unittest.mock import patch, MagicMock


@patch('kafka_producer.get_producer')
def test_send_notification_sent_calls_producer(mock_get_producer):
    mock_instance = MagicMock()
    mock_get_producer.return_value = mock_instance

    from kafka_producer import send_notification_sent

    send_notification_sent("notif_123", 456)

    mock_instance.send.assert_called_once()
    args, kwargs = mock_instance.send.call_args
    assert args[0] == 'notification.sent'
    assert args[1]['notification_id'] == "notif_123"
    assert args[1]['order_id'] == 456
    assert args[1]['status'] == 'sent'


@patch('postmark_client.client')
def test_send_ticket_email_calls_postmark(mock_client):
    from postmark_client import send_ticket_email

    send_ticket_email("test@example.com", 1, 10, 100)

    mock_client.emails.send.assert_called_once()
    args, kwargs = mock_client.emails.send.call_args
    assert kwargs['To'] == "test@example.com"
    assert "1" in kwargs['Subject']


@patch('postmark_client.client')
def test_send_error_email_calls_postmark(mock_client):
    from postmark_client import send_error_email

    send_error_email("test@example.com", 2, "Insufficient funds")

    mock_client.emails.send.assert_called_once()
    args, kwargs = mock_client.emails.send.call_args
    assert kwargs['To'] == "test@example.com"
    assert "Insufficient funds" in kwargs['HtmlBody']


@patch('postmark_client.client')
def test_send_refund_email_calls_postmark(mock_client):
    from postmark_client import send_refund_email

    send_refund_email("test@example.com", 3, 30, 500.0)

    mock_client.emails.send.assert_called_once()
    args, kwargs = mock_client.emails.send.call_args
    assert kwargs['To'] == "test@example.com"