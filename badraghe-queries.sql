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

-- Query 3
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    u.email,
    DATE_FORMAT(p.payment_date, '%Y-%m') AS month,
    SUM(p.amount) AS total_payments
FROM users u
STRAIGHT_JOIN payments p FORCE INDEX (idx_payments_user_id) ON u.id = p.user_id
GROUP BY u.id, month
ORDER BY u.id, month;

-- Query 4
SELECT 
    u.first_name,
    u.last_name,
    tt.departure_city
FROM users u
JOIN (
    SELECT user_id, departure_city
    FROM user_reservations ur
    JOIN travel_tickets tt FORCE INDEX (idx_travel_tickets_departure_city) ON ur.ticket_id = tt.id
    GROUP BY user_id, departure_city
    HAVING COUNT(*) = 1
) single_tickets ON u.id = single_tickets.user_id
JOIN travel_tickets tt ON single_tickets.departure_city = tt.departure_city;

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

-- Query 9
SELECT 
    tt.departure_city,
    COUNT(*) AS tickets_sold
FROM travel_tickets tt USE INDEX (idx_fulltext_departure_city)
JOIN user_reservations ur ON tt.id = ur.ticket_id
WHERE MATCH(tt.departure_city) AGAINST('Tehran' IN BOOLEAN MODE)
AND ur.status != 'canceled'
GROUP BY tt.departure_city;

-- Query 10
SELECT DISTINCT tt.departure_city
FROM travel_tickets tt
JOIN user_reservations ur ON tt.id = ur.ticket_id
WHERE ur.user_id = (
    SELECT id FROM users 
    ORDER BY created_at ASC 
    LIMIT 1
);

-- Query 11
SELECT 
    STRAIGHT_JOIN u.first_name, u.last_name
FROM roles r
JOIN user_role ur ON r.id = ur.role_id
JOIN users u ON ur.user_id = u.id
WHERE r.name = 'Support';

-- Query 12
SELECT 
    u.first_name,
    u.last_name
FROM users u
WHERE (
    SELECT COUNT(*) 
    FROM user_reservations ur 
    WHERE ur.user_id = u.id AND ur.status = 'paid'
) >= 2;

-- Query 13
SELECT 
    u.first_name,
    u.last_name,
    tt.transport_type,
    COUNT(*) AS ticket_count
FROM users u
JOIN user_reservations ur ON u.id = ur.user_id
JOIN travel_tickets tt FORCE INDEX (idx_travel_tickets_transport_type) ON ur.ticket_id = tt.id
GROUP BY u.id, tt.transport_type
HAVING COUNT(*) <= 2;

-- Query 14
SELECT DISTINCT u.email, u.phone
FROM users u
JOIN (
    SELECT ur.user_id
    FROM user_reservations ur
    JOIN travel_tickets tt ON ur.ticket_id = tt.id
    GROUP BY ur.user_id
    HAVING COUNT(DISTINCT tt.transport_type) = 3
) all_types ON u.id = all_types.user_id;

-- Query 15
SELECT 
    tt.*,
    ur.reserved_at
FROM travel_tickets tt
JOIN user_reservations ur FORCE INDEX (idx_user_reservations_reserved_at) ON tt.id = ur.ticket_id
WHERE ur.reserved_at >= CURDATE()
AND ur.reserved_at < CURDATE() + INTERVAL 1 DAY
ORDER BY ur.reserved_at;

-- Query 18
SET @top_canceler_id = (
    SELECT user_id
    FROM user_reservations
    WHERE status = 'canceled'
    GROUP BY user_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
);

UPDATE users 
SET last_name = 'Redington'
WHERE id = @top_canceler_id;

-- Query 19
DELETE ur FROM user_reservations ur
JOIN users u ON ur.user_id = u.id
WHERE u.last_name = 'Redington' 
AND ur.status = 'canceled';

-- Query 20
DELETE FROM user_reservations 
WHERE status = 'canceled';

-- Query 21
UPDATE travel_tickets tt
STRAIGHT_JOIN flight_details fd ON tt.id = fd.ticket_id
STRAIGHT_JOIN user_reservations ur ON tt.id = ur.ticket_id
SET tt.price = tt.price * 0.9
WHERE fd.airline_name = 'MahanAir' 
AND ur.reserved_at >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)
AND ur.reserved_at < CURDATE();

-- Query 22
CREATE TEMPORARY TABLE temp_report_counts AS
SELECT category, COUNT(*) AS report_count
FROM reports
GROUP BY category;

SELECT category, report_count
FROM temp_report_counts
ORDER BY report_count DESC
LIMIT 1;

DROP TEMPORARY TABLE temp_report_counts;