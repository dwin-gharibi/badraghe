-- Query 1
SELECT u.id, u.first_name, u.last_name, u.email
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM user_reservations ur 
    WHERE ur.user_id = u.id
);