from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, conint
from datetime import datetime
from app.db import connect_db, close_db, execute_query
from app.utils.auth_util import get_current_user, require_roles

router = APIRouter(prefix="/reviews")

class ReviewCreate(BaseModel):
    ticket_id: int
    rating: conint(ge=1, le=5)
    review_text: Optional[str] = None

class ReviewUpdate(BaseModel):
    rating: Optional[conint(ge=1, le=5)] = None
    review_text: Optional[str] = None

class ReviewOut(BaseModel):
    id: int
    user_id: int
    ticket_id: int
    rating: int
    review_text: Optional[str]
    created_at: datetime
    updated_at: datetime

class ReviewStatsOut(BaseModel):
    ticket_id: int
    total_reviews: int
    average_rating: float

async def get_review_by_id(review_id: int):
    await connect_db()
    review = await execute_query(
        "SELECT * FROM reviews WHERE id = %s",
        (review_id,),
        fetch_one=True
    )
    await close_db()
    return review

@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    await connect_db()
    try:
        review_id = await execute_query(
            """
            INSERT INTO reviews (user_id, ticket_id, rating, review_text)
            VALUES (%s, %s, %s, %s)
            """,
            (
                current_user["user_id"],
                review.ticket_id,
                review.rating,
                review.review_text
            ),
            return_lastrowid=True,
            fetch_one=True
        )
        new_review = await execute_query(
            "SELECT * FROM reviews WHERE id = %s",
            (review_id,),
            fetch_one=True
        )
        await close_db()
        return new_review
    except Exception as e:
        await close_db()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ReviewOut])
async def list_reviews(
    ticket_id: Optional[int] = None,
    user_id: Optional[int] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    ticket_status: Optional[str] = None,
    review_status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    await connect_db()
    query = """
        SELECT r.* FROM reviews r
        JOIN travel_tickets t ON r.ticket_id = t.id
        WHERE 1=1
    """
    params = []

    if ticket_id:
        query += " AND r.ticket_id = %s"
        params.append(ticket_id)
    if user_id:
        query += " AND r.user_id = %s"
        params.append(user_id)
    if min_rating:
        query += " AND r.rating >= %s"
        params.append(min_rating)
    if max_rating:
        query += " AND r.rating <= %s"
        params.append(max_rating)
    if ticket_status:
        query += " AND t.status = %s"
        params.append(ticket_status)
    if review_status == "has_text":
        query += " AND r.review_text IS NOT NULL AND r.review_text != ''"
    elif review_status == "no_text":
        query += " AND (r.review_text IS NULL OR r.review_text = '')"
    if from_date:
        query += " AND r.created_at >= %s"
        params.append(from_date)
    if to_date:
        query += " AND r.created_at <= %s"
        params.append(to_date)

    query += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    reviews = await execute_query(query, params, fetch_all=True)
    await close_db()
    return reviews

@router.get("/{review_id}", response_model=ReviewOut)
async def get_review(review_id: int):
    review = await get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.get("/user/{user_id}", response_model=List[ReviewOut])
async def get_reviews_by_user(user_id: int):
    return await list_reviews(user_id=user_id)

@router.get("/ticket/{ticket_id}", response_model=List[ReviewOut])
async def get_reviews_by_ticket(ticket_id: int):
    return await list_reviews(ticket_id=ticket_id)

@router.get("/ticket/{ticket_id}/stats", response_model=ReviewStatsOut)
async def get_ticket_review_stats(ticket_id: int):
    await connect_db()
    stats = await execute_query(
        """
        SELECT ticket_id, COUNT(*) AS total_reviews, ROUND(AVG(rating), 2) AS average_rating
        FROM reviews
        WHERE ticket_id = %s
        GROUP BY ticket_id
        """,
        (ticket_id,),
        fetch_one=True
    )
    await close_db()
    if not stats:
        raise HTTPException(status_code=404, detail="No reviews found for this ticket")
    return stats

@router.patch("/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: dict = Depends(get_current_user)
):
    review = await get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    update_data = review_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join(f"{field} = %s" for field in update_data)
    values = list(update_data.values())
    values.append(review_id)

    await connect_db()
    await execute_query(
        f"UPDATE reviews SET {set_clause} WHERE id = %s",
        values,
        commit=True
    )
    updated_review = await execute_query(
        "SELECT * FROM reviews WHERE id = %s",
        (review_id,),
        fetch_one=True
    )
    await close_db()
    return updated_review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: dict = Depends(get_current_user)
):
    review = await get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    await connect_db()
    await execute_query(
        "DELETE FROM reviews WHERE id = %s",
        (review_id,),
        commit=True
    )
    await close_db()
    return

@router.head("/{review_id}")
async def head_review(review_id: int):
    review = await get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404)
    return