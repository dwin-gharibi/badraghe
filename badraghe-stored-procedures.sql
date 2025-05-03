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

CREATE PROCEDURE get_users_with_canceled_reservations_by_support(IN support_contact VARCHAR(100))
BEGIN
    SELECT DISTINCT
        u.id,
        u.first_name,
        u.last_name,
        u.email,
        u.phone
    FROM users u
    JOIN user_reservations ur ON u.id = ur.user_id
    JOIN ticket_cancellations tc ON ur.id = tc.reservation_id
    JOIN users support ON tc.canceled_by = support.id
    WHERE support.email = support_contact OR support.phone = support_contact;
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
