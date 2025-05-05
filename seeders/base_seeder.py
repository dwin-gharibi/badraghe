import pymysql
from dotenv import load_dotenv
from pymysql.err import IntegrityError, OperationalError, DataError
import os
from faker import Faker

load_dotenv()

class BaseSeeder:
    def __init__(self):
        self.connection = pymysql.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'user'),
            password=os.getenv('DB_PASSWORD', 'password'),
            database=os.getenv('DB_NAME', 'badrage_database'),
            port=int(os.getenv('DB_PORT', 3306)),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        self.fake = Faker()

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except (IntegrityError, DataError, OperationalError) as e:
            return None

    def execute_many(self, query, data):
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(query, data)
                return cursor.rowcount
        except (IntegrityError, DataError, OperationalError) as e:
            return 0

    def fetch_all(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Exception as e:
            return []

    def fetch_one(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Exception as e:
            return None

    def get_random_ids(self, table, limit=10):
        query = f"SELECT id FROM {table} ORDER BY RAND() LIMIT %s"
        result = self.fetch_all(query, (limit,))
        return [row['id'] for row in result] if result else []

    def close(self):
        try:
            self.connection.close()
        except Exception as e:
            pass