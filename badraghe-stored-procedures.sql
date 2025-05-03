-- Stored Procedure 1
DELIMITER //

CREATE PROCEDURE GetUserTickets(IN user_contact VARCHAR(100))
BEGIN
    SELECT 
        tt.*,
        ur.reserved_at
    FROM users u
    JOIN user_reservations ur FORCE INDEX (idx_user_reservations_user_id) ON u.id = ur.user_id
    JOIN travel_tickets tt ON ur.ticket_id = tt.id
    WHERE u.email = user_contact OR u.phone = user_contact
    ORDER BY ur.reserved_at;
END //

-- Stored Procedure 2
DELIMITER //

CREATE PROCEDURE GetUsersWithCancelledBookings(IN identifier VARCHAR(100))
BEGIN
    SELECT u.full_name
    FROM users u
    WHERE EXISTS (
        SELECT 1
        FROM cancellations c
        JOIN travel_tickets t ON c.ticket_id = t.id
        JOIN support_staff s ON s.id = c.support_id
        WHERE t.user_id = u.id AND (s.email = identifier OR s.phone = identifier)
    );
END //

-- Stored Procedure 3
DELIMITER //

CREATE PROCEDURE GetTicketsByCity(IN city_name VARCHAR(100))
BEGIN
    SELECT 
        tt.*,
        u.first_name,
        u.last_name
    FROM travel_tickets tt
    JOIN user_reservations ur ON tt.id = ur.ticket_id
    JOIN users u ON ur.user_id = u.id
    WHERE tt.departure_city = city_name;
END //

-- Stored Procedure 4
DELIMITER //

CREATE PROCEDURE SearchTicketsByKeyword(IN keyword VARCHAR(100))
BEGIN
    SELECT t.*
    FROM travel_tickets t
    JOIN user_reservations ur ON ur.ticket_id = t.id
    JOIN users u ON u.id = ur.user_id
    WHERE MATCH(u.first_name, u.last_name) AGAINST (keyword IN NATURAL LANGUAGE MODE)
       OR MATCH(t.departure_city, t.arrival_city, t.class_type) AGAINST (keyword IN NATURAL LANGUAGE MODE);
END //

-- Stored Procedure 5
DELIMITER //

CREATE PROCEDURE GetOtherUsersFromSameCity(IN contactInfo VARCHAR(100))
BEGIN
    SELECT u.first_name, u.last_name, u.email, u.phone, u.city
    FROM users u
    WHERE u.city = (SELECT city FROM users WHERE email = contactInfo OR phone = contactInfo)
    AND (u.email != contactInfo AND u.phone != contactInfo);
END //

-- Stored Procedure 8
DELIMITER //

CREATE PROCEDURE GetUsersWithMostReports(IN report_subject VARCHAR(50))
BEGIN
    CREATE TEMPORARY TABLE temp_user_reports AS
    SELECT 
        u.id,
        u.first_name,
        u.last_name,
        COUNT(*) AS report_count
    FROM users u
    JOIN reports r ON u.id = r.user_id
    WHERE r.category = report_subject
    GROUP BY u.id;
    
    SELECT first_name, last_name, report_count
    FROM temp_user_reports
    ORDER BY report_count DESC;
    
    DROP TEMPORARY TABLE temp_user_reports;
END //
