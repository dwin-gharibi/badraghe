import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mysql_host: str = os.getenv("MYSQL_HOST")
    mysql_user: str = os.getenv("MYSQL_USER")
    mysql_port: int = os.getenv("MYSQL_PORT")
    mysql_password: str = os.getenv("MYSQL_PASSWORD")
    mysql_db: str = os.getenv("MYSQL_DB")

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
