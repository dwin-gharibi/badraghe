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