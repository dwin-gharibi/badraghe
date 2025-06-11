from app.tasks.reservation_task import cancel_expired_reservation

def schedule_reservation_cancellation(reservation_id: int, delay_seconds: int = 600):
    cancel_expired_reservation.apply_async(
        args=[reservation_id],
        countdown=delay_seconds
    )
