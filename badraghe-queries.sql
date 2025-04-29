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
-- Query 5
SELECT 
    u.*
FROM users u
JOIN user_reservations ur FORCE INDEX (idx_user_reservations_reserved_at) ON u.id = ur.user_id
ORDER BY ur.reserved_at DESC
LIMIT 1;
