from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('travel_tickets', dependencies=['service_providers'])
class TravelTicketSeeder(BaseSeeder):
    def seed(self, count=10):
        ticket_faker = get_faker('travel_tickets')
        provider_ids = self.get_random_ids('service_providers', 5)
        
        tickets_data = [ticket_faker(self.fake, provider_ids) for _ in range(count)]
        
        insert_query = """
        INSERT INTO travel_tickets (
            transport_type, departure_city, arrival_city, departure_time, arrival_time,
            price, currency, available_seats, total_seats, transport_company_id, class_type, status
        ) VALUES (
            %(transport_type)s, %(departure_city)s, %(arrival_city)s, %(departure_time)s, %(arrival_time)s,
            %(price)s, %(currency)s, %(available_seats)s, %(total_seats)s, %(transport_company_id)s,
            %(class_type)s, %(status)s
        )
        """
        
        inserted_count = self.execute_many(insert_query, tickets_data)
        return inserted_count