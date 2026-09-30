"""
Hotel routes: /hotels
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import Hotel
from ml.hotel_recommender import recommend_hotels
from ml.datasets import load_hotels_df

router = APIRouter()


@router.get("/")
def list_hotels(
    city: Optional[str] = Query(None),
    min_stars: int = Query(1, ge=1, le=5),
    max_price: Optional[float] = Query(None),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
):
    """List hotels with optional filters."""
    query = db.query(Hotel).filter(Hotel.is_active == True)  # noqa: E712
    if city:
        query = query.filter(Hotel.city.ilike(f"%{city}%"))
    if min_stars:
        query = query.filter(Hotel.star_rating >= min_stars)
    if max_price:
        query = query.filter(Hotel.price_per_night <= max_price)

    rows = query.order_by(Hotel.user_rating.desc()).limit(limit).all()

    if not rows:
        df = load_hotels_df()
        if city:
            df = df[df["city"].str.lower().str.contains(city.lower(), na=False)]
        if max_price:
            df = df[df["price_per_night"] <= max_price]
        df = df[df["star_rating"] >= min_stars]
        return df.head(limit).to_dict(orient="records")

    return [
        {
            "id": str(h.id), "name": h.name, "city": h.city, "address": h.address,
            "latitude": h.latitude, "longitude": h.longitude,
            "star_rating": h.star_rating, "user_rating": h.user_rating,
            "price_per_night": h.price_per_night, "amenities": h.amenities,
            "image_url": h.image_url, "phone": h.phone, "website": h.website,
        }
        for h in rows
    ]


class HotelRecommendRequest(BaseModel):
    city: str
    budget_per_night: float
    latitude: float
    longitude: float
    min_star_rating: int = 3
    amenities: Optional[List[str]] = None
    top_n: int = 5


@router.post("/recommend")
def recommend(
    payload: HotelRecommendRequest,
    db: Session = Depends(get_db),
):
    """Get hotel recommendations based on budget, location, and preferences."""
    rows = db.query(Hotel).filter(
        Hotel.is_active == True,  # noqa: E712
        Hotel.city.ilike(f"%{payload.city}%"),
    ).all()

    if rows:
        hotels = [
            {
                "id": str(h.id), "name": h.name, "city": h.city,
                "latitude": h.latitude, "longitude": h.longitude,
                "star_rating": h.star_rating, "user_rating": h.user_rating,
                "price_per_night": h.price_per_night, "amenities": h.amenities or [],
                "image_url": h.image_url, "phone": h.phone, "website": h.website,
            }
            for h in rows
        ]
    else:
        df = load_hotels_df()
        df = df[df["city"].str.lower().str.contains(payload.city.lower(), na=False)]
        hotels = df.to_dict(orient="records")

    return recommend_hotels(
        hotels=hotels,
        budget_per_night=payload.budget_per_night,
        latitude=payload.latitude,
        longitude=payload.longitude,
        min_star_rating=payload.min_star_rating,
        required_amenities=payload.amenities,
        top_n=payload.top_n,
    )
