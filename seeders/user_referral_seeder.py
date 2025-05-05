from .base_seeder import BaseSeeder
from decorators.registry import get_faker, register_seeder

@register_seeder('user_referrals', dependencies=['users'])
class UserReferralSeeder(BaseSeeder):
    def seed(self, count=10):
        referral_faker = get_faker('user_referrals')
        user_ids = self.get_random_ids('users', min(count*2, 20))
        
        if len(user_ids) < 2:
            return 0

        data = []
        for i in range(0, len(user_ids)-1, 2):
            data.append(referral_faker(self.fake, [user_ids[i], user_ids[i+1]]))

        query = """
        INSERT INTO user_referrals (
            referrer_id, referred_id
        ) VALUES (
            %(referrer_id)s, %(referred_id)s
        )
        """
        
        inserted = self.execute_many(query, data[:count])
        return inserted