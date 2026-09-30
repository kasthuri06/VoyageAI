"""
Review routes: /reviews
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.session import get_db
from database.models import Review, TouristPlace, User
from schemas.trip import ReviewCreate, ReviewOut
from core.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=ReviewOut, status_code=201)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a review."""
    if not any([payload.place_id, payload.hotel_id, payload.restaurant_id]):
        raise HTTPException(status_code=400, detail="Provide place_id, hotel_id, or restaurant_id")
    if not (1.0 <= payload.rating <= 5.0):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    review = Review(
        user_id=str(current_user.id),
        place_id=str(payload.place_id) if payload.place_id else None,
        hotel_id=str(payload.hotel_id) if payload.hotel_id else None,
        restaurant_id=str(payload.restaurant_id) if payload.restaurant_id else None,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)

    if payload.place_id:
        place = db.query(TouristPlace).filter(TouristPlace.id == str(payload.place_id)).first()
        if place:
            place.total_reviews += 1
            avg = db.query(func.avg(Review.rating)).filter(
                Review.place_id == str(payload.place_id)
            ).scalar()
            place.rating = round(float(avg or payload.rating), 2)

    db.commit()
    db.refresh(review)
    return ReviewOut(
        id=review.id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        username=current_user.username,
    )


@router.get("/place/{place_id}")
def get_place_reviews(place_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Get all reviews for a tourist place."""
    reviews = (
        db.query(Review, User.username)
        .join(User, Review.user_id == User.id)
        .filter(Review.place_id == place_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(r.id), "rating": r.rating, "comment": r.comment,
            "username": username, "created_at": r.created_at.isoformat(),
        }
        for r, username in reviews
    ]
