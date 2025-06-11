from app.celery_app import celery
from app.db import execute_query, connect_db, close_db
import logging
logger = logging.getLogger(__name__)


@celery.task(name="cancel_expired_reservation")
def cancel_expired_reservation(reservation_id: int):
    import asyncio

    logger.info(f"Running cancel_expired_reservation with ID: {reservation_id}")

    async def inner():
        await connect_db()

        reservation = await execute_query(
            "SELECT status, ticket_id FROM user_reservations WHERE id = %s",
            (reservation_id,),
            fetch_one=True
        )

        if reservation and reservation["status"] == "temporary":
            await execute_query(
                "UPDATE user_reservations SET status = 'canceled', updated_at = NOW() WHERE id = %s",
                (reservation_id,),
                commit=True
            )

            await execute_query(
                "UPDATE travel_tickets SET available_seats = available_seats + 1 WHERE id = %s",
                (reservation["ticket_id"],),
                commit=True
            )

        await close_db()

    asyncio.run(inner())
