import firebase_admin
from firebase_admin import credentials, messaging
import logging

_logger = logging.getLogger(__name__)
firebase_app = None


def send_firebase_push(fcm_token, title, body, service_account_path):
    global firebase_app
    if not firebase_app:
        cred = credentials.Certificate(service_account_path)
        firebase_app = firebase_admin.initialize_app(cred)
    # Create the message payload
    message = messaging.Message(
        token=fcm_token,
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        android=messaging.AndroidConfig(priority="high"),
    )
    _logger.info(f"This is the Notification I want to send", message)
    response = messaging.send(message)
    return {"message_id": response}
