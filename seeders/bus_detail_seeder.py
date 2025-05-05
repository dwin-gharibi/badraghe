from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('bus_details', dependencies=['travel_tickets'])
class BusDetailSeeder(BaseSeeder):
    def seed(self, count=10):
        bus_faker = get_faker('bus_details')
        ticket_ids = self.get_random_ids('travel_tickets', min(count, 20))
        
        if not ticket_ids:
            return 0

        data = []
        for ticket_id in ticket_ids[:count]:
            data.append(bus_faker(self.fake, [ticket_id]))

        query = """
        INSERT INTO bus_details (
            ticket_id, bus_company, bus_type, seats_per_row
        ) VALUES (
            %(ticket_id)s, %(bus_company)s, %(bus_type)s, %(seats_per_row)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted