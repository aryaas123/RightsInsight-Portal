import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "yourmail@gmail.com"
APP_PASSWORD = "your_app_password"

def send_email(receiver, subject, content):
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
