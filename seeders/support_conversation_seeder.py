from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('support_ticket_conversations', dependencies=['support_tickets', 'users'])
class SupportConversationSeeder(BaseSeeder):
    def seed(self, count=10):
        conversation_faker = get_faker('support_conversations')
        ticket_ids = self.get_random_ids('support_tickets', min(count, 10))
        user_ids = self.get_random_ids('users', min(count, 10))
        
        if not ticket_ids or not user_ids:
            return 0

        data = []
        for _ in range(count):
            data.append(conversation_faker(self.fake, ticket_ids, user_ids))

        query = """
        INSERT INTO support_ticket_conversations (
            ticket_id, user_id, message, message_type
        ) VALUES (
            %(ticket_id)s, %(user_id)s, %(message)s, %(message_type)s
        )
        """
        
        inserted = self.execute_many(query, data)
        return inserted