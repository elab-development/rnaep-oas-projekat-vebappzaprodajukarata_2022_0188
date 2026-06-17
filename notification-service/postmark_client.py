import os
from postmarker.core import PostmarkClient
from dotenv import load_dotenv

load_dotenv()

client = PostmarkClient(server_token=os.getenv("POSTMARK_API_KEY"))

def send_ticket_email(to_email, order_id, reservation_id, payment_id):
    # Šaljemo email sa potvrdom kupovine ulaznice
    client.emails.send(
        From=os.getenv("POSTMARK_FROM_EMAIL"),
        To=to_email,
        Subject=f"Potvrda kupovine ulaznice - Porudžbina #{order_id}",
        HtmlBody=f"""
            <h1>Hvala na kupovini!</h1>
            <p>Vaša porudžbina #{order_id} je uspešno obrađena.</p>
            <p>ID rezervacije: {reservation_id}</p>
            <p>ID plaćanja: {payment_id}</p>
        """
    )

def send_error_email(to_email, order_id, error_message):
    # Šaljemo email o neuspjelom plaćanju
    client.emails.send(
        From=os.getenv("POSTMARK_FROM_EMAIL"),
        To=to_email,
        Subject=f"Neuspelo plaćanje - Porudžbina #{order_id}",
        HtmlBody=f"""
            <h1>Plaćanje nije uspelo</h1>
            <p>Nažalost, vaše plaćanje za porudžbinu #{order_id} nije uspelo.</p>
            <p>Razlog: {error_message}</p>
            <p>Molimo pokušajte ponovo.</p>
        """
    )

def send_refund_email(to_email, payment_id, refund_id, amount):
    # Šaljemo email o uspješnoj refundaciji
    client.emails.send(
        From=os.getenv("POSTMARK_FROM_EMAIL"),
        To=to_email,
        Subject=f"Potvrda refundacije - Plaćanje #{payment_id}",
        HtmlBody=f"""
            <h1>Refundacija uspešna</h1>
            <p>Vaša refundacija za plaćanje #{payment_id} je uspešno obrađena.</p>
            <p>ID refundacije: {refund_id}</p>
            <p>Iznos: {amount}</p>
        """
    )