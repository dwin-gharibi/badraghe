from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from app.config import settings

def send_otp_email(to_address, subject, otp):
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 30px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 20px;">
                <div style="text-align: center;">
                    <img src="https://api.badraghe.dwin.codes/static/logo.png" alt="Logo" width="120" style="margin-bottom: 20px;" />
                    <h2 style="color: #333333;">Your Verification Code</h2>
                </div>
                <p style="font-size: 16px; color: #555555;">Hello,</p>
                <p style="font-size: 16px; color: #555555;">
                    Your OTP code is:
                    <strong style="font-size: 20px; color: #000000;">{otp}</strong>
                </p>
                <p style="font-size: 14px; color: #999999;">This code is valid for 5 minutes.</p>
                <br>
                <p style="font-size: 14px; color: #555555;">Thank you,<br>Badraghe</p>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = settings.mail_from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(settings.mail_host, settings.mail_port)
        server.starttls()
        server.login(settings.mail_user, settings.mail_password)
        server.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print("Failed to send email:", e)
    finally:
        server.quit()
