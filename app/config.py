import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mysql_host: str = os.getenv("MYSQL_HOST")
    mysql_user: str = os.getenv("MYSQL_USER")
    mysql_port: int = os.getenv("MYSQL_PORT")
    mysql_password: str = os.getenv("MYSQL_PASSWORD")
    mysql_db: str = os.getenv("MYSQL_DB")

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    celery_broker_url: str = redis_url
    celery_result_backend: str = redis_url

    mail_host: str = os.getenv("MAIL_HOST", "smtp.c1.liara.email")
    mail_port: int = int(os.getenv("MAIL_PORT", 465))
    mail_user: str = os.getenv("MAIL_USER", "")
    mail_password: str = os.getenv("MAIL_PASSWORD", "")
    mail_from_address: str = os.getenv("MAIL_FROM_ADDRESS", "")
    mail_form_name: str = os.getenv("MAIL_FROM_NAME", "")

    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: int = int(os.getenv("REDIS_PORT"))
    redis_db: int = int(os.getenv("REDIS_DB"))

    jwt_expiration_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    jwt_secret: str = os.getenv("JWT_SECTET")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")

    sms_ir_api_key: str = os.getenv("SMS_IR_API_KEY")
    sms_ir_line_number: str = os.getenv("SMS_IR_LINE_NUMBER")

    otp_expiration_seconds: int = 300

settings = Settings()
