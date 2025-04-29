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

-- Query 6
SET @avg_payments = (
    SELECT AVG(total_payments)
    FROM (
        SELECT SUM(amount) AS total_payments
        FROM payments
        GROUP BY user_id
    ) avg_payments
);

SELECT
    u.email,
    u.phone
FROM users u
JOIN (
    SELECT user_id, SUM(amount) AS total_payments
    FROM payments
    GROUP BY user_id
    HAVING total_payments > @avg_payments
) higher_users ON u.id = higher_users.user_id;

-- Query 7
SELECT 
    tt.transport_type,
    COUNT(*) AS tickets_sold
FROM travel_tickets tt FORCE INDEX (idx_travel_tickets_transport_type)
JOIN user_reservations ur FORCE INDEX (idx_user_reservations_status) ON tt.id = ur.ticket_id
WHERE ur.status != 'canceled'
GROUP BY tt.transport_type;

-- Query 8
SELECT 
    u.first_name,
    u.last_name,
    COUNT(*) AS tickets_purchased
FROM users u
JOIN user_reservations ur FORCE INDEX (idx_user_reservations_status) ON u.id = ur.user_id
WHERE ur.reserved_at >= DATE_SUB(NOW(), INTERVAL 1 WEEK)
AND ur.status = 'paid'
GROUP BY u.id
ORDER BY tickets_purchased DESC
LIMIT 3;