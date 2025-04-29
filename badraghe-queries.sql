-- Query 1
SELECT u.first_name, u.last_name
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM user_reservations ur 
    WHERE ur.user_id = u.id
);
-- Query 2
SELECT u.first_name, u.last_name
FROM users u
WHERE EXISTS (
    SELECT 1 FROM user_reservations ur 
    WHERE ur.user_id = u.id
);
