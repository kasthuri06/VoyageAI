"""
Restaurant routes: /restaurants
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import Restaurant
from ml.restaurant_recommender import recommend_restaurants
from ml.datasets import load_restaurants_df

router = APIRouter()


@router.get("/")
def list_restaurants(
    city: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    min_rating: float = Query(0.0, ge=0, le=5),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
):
    """List restaurants with optional filters."""
    query = db.query(Restaurant).filter(Restaurant.is_active == True)  # noqa: E712
    if city:
        query = query.filter(Restaurant.city.ilike(f"%{city}%"))
    if cuisine:
        query = query.filter(Restaurant.cuisine.ilike(f"%{cuisine}%"))
    if min_rating:
        query = query.filter(Restaurant.rating >= min_rating)

    rows = query.order_by(Restaurant.rating.desc()).limit(limit).all()

    if not rows:
        df = load_restaurants_df()
        if city:
            df = df[df["city"].str.lower().str.contains(city.lower(), na=False)]
        if cuisine:
            df = df[df["cuisine"].str.lower().str.contains(cuisine.lower(), na=False)]
        df = df[df["rating"] >= min_rating]
        return df.head(limit).to_dict(orient="records")

    return [
        {
            "id": str(r.id), "name": r.name, "city": r.city, "address": r.address,
            "latitude": r.latitude, "longitude": r.longitude, "cuisine": r.cuisine,
            "rating": r.rating, "price_range": r.price_range,
            "avg_cost_for_two": r.avg_cost_for_two,
            "opening_hours": r.opening_hours, "image_url": r.image_url, "phone": r.phone,
        }
        for r in rows
    ]


class RestaurantRecommendRequest(BaseModel):
    latitude: float
    longitude: float
    budget_for_two: Optional[float] = None
    preferred_cuisines: Optional[List[str]] = None
    min_rating: float = 3.5
    top_n: int = 5
    radius_km: float = 3.0


@router.post("/recommend")
def recommend(
    payload: RestaurantRecommendRequest,
    db: Session = Depends(get_db),
):
    """Get restaurant recommendations based on location and preferences."""
    rows = db.query(Restaurant).filter(Restaurant.is_active == True).all()  # noqa: E712
    if rows:
        restaurants = [
            {
                "id": str(r.id), "name": r.name, "city": r.city,
                "latitude": r.latitude, "longitude": r.longitude,
                "cuisine": r.cuisine, "rating": r.rating,
                "avg_cost_for_two": r.avg_cost_for_two,
                "price_range": r.price_range, "opening_hours": r.opening_hours,
                "image_url": r.image_url, "phone": r.phone,
            }
            for r in rows
        ]
    else:
        restaurants = load_restaurants_df().to_dict(orient="records")

    return recommend_restaurants(
        restaurants=restaurants,
        latitude=payload.latitude,
        longitude=payload.longitude,
        budget_for_two=payload.budget_for_two,
        preferred_cuisines=payload.preferred_cuisines,
        min_rating=payload.min_rating,
        top_n=payload.top_n,
        radius_km=payload.radius_km,
    )
