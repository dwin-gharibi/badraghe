from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('users')
class UserSeeder(BaseSeeder):
    def seed(self, count=10):
        user_faker = get_faker('users')
        users_data = [user_faker(self.fake) for _ in range(count)]
        
        insert_query = """
        INSERT INTO users (
            first_name, last_name, email, phone, password, country, state, city, 
            address, zip_code, date_of_birth, gender, profile_picture_url, 
            status, is_verified, bio, preferences, last_login
        ) VALUES (
            %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(password)s, 
            %(country)s, %(state)s, %(city)s, %(address)s, %(zip_code)s, 
            %(date_of_birth)s, %(gender)s, %(profile_picture_url)s, %(status)s, 
            %(is_verified)s, %(bio)s, %(preferences)s, %(last_login)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, users_data)
        return inserted_count