import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ssl import create_default_context
from app.config import settings

def send_email(to_address, subject, body):
    try:
        context = create_default_context()

        with smtplib.SMTP_SSL(settings.mail_host, settings.mail_port, context=context) as server:
            server.login(settings.mail_user, settings.mail_password)

            msg = MIMEMultipart()
            msg['From'] = f"{settings.mail_form_name} <{settings.mail_from_address}>"
            msg['To'] = to_address
            msg['Subject'] = subject
            msg.add_header('x-liara-tag', 'test-tag')
            msg.attach(MIMEText(body, 'plain'))

            server.sendmail(settings.mail_from_address, to_address, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
