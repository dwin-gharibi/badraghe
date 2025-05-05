from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('flight_details', dependencies=['travel_tickets'])
class FlightDetailSeeder(BaseSeeder):
    def seed(self, count=10):
        flight_faker = get_faker('flight_details')
        ticket_ids = self.get_random_ids('travel_tickets', min(count, 20))
        
        if not ticket_ids:
            return 0

        data = []
        for ticket_id in ticket_ids[:count]:
            data.append(flight_faker(self.fake, [ticket_id]))

        query = """
        INSERT INTO flight_details (
            ticket_id, airline_name, flight_class, stops, 
            flight_number, departure_airport, arrival_airport
        ) VALUES (
            %(ticket_id)s, %(airline_name)s, %(flight_class)s, %(stops)s,
            %(flight_number)s, %(departure_airport)s, %(arrival_airport)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted