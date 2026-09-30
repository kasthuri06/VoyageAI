"""
Recommendation routes: /recommend
Full ML pipeline: input → feature eng → model → route opt → weather → itinerary

City search priority:
  1. PostgreSQL database (if populated)
  2. Local CSV dataset
  3. Groq AI generation (for any Indian city not in CSV)
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import TouristPlace, Hotel, Restaurant, UserHistory, User
from schemas.recommend import RecommendationRequest
from core.dependencies import get_current_user
from ml.itinerary_generator import generate_itinerary
from ml.recommendation_engine import get_recommender
from ml.datasets import load_places_df, load_hotels_df, load_restaurants_df
from ml.groq_service import (
    generate_places_for_city,
    generate_hotels_for_city,
    generate_restaurants_for_city,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Data loaders — DB → CSV → Groq fallback chain
# ---------------------------------------------------------------------------

def _db_places_to_dicts(db: Session) -> List[dict]:
    rows = db.query(TouristPlace).filter(TouristPlace.is_active == True).all()  # noqa
    if rows:
        return [
            {
                "id": str(r.id), "name": r.name, "description": r.description,
                "city": r.city, "state": r.state, "country": r.country,
                "latitude": r.latitude, "longitude": r.longitude,
                "category": r.category, "tags": r.tags or [],
                "rating": r.rating, "entry_fee": r.entry_fee,
                "opening_hours": r.opening_hours, "is_indoor": r.is_indoor,
                "estimated_duration_hours": r.estimated_duration_hours,
                "best_time_to_visit": r.best_time_to_visit,
                "image_url": r.image_url,
            }
            for r in rows
        ]
    df = load_places_df()
    return df.to_dict(orient="records") if not df.empty else []


def _db_hotels_to_dicts(db: Session) -> List[dict]:
    rows = db.query(Hotel).filter(Hotel.is_active == True).all()  # noqa
    if rows:
        return [
            {
                "id": str(r.id), "name": r.name, "city": r.city,
                "address": r.address, "latitude": r.latitude, "longitude": r.longitude,
                "star_rating": r.star_rating, "user_rating": r.user_rating,
                "price_per_night": r.price_per_night, "amenities": r.amenities or [],
                "image_url": r.image_url, "phone": r.phone, "website": r.website,
            }
            for r in rows
        ]
    df = load_hotels_df()
    return df.to_dict(orient="records") if not df.empty else []


def _db_restaurants_to_dicts(db: Session) -> List[dict]:
    rows = db.query(Restaurant).filter(Restaurant.is_active == True).all()  # noqa
    if rows:
        return [
            {
                "id": str(r.id), "name": r.name, "city": r.city,
                "address": r.address, "latitude": r.latitude, "longitude": r.longitude,
                "cuisine": r.cuisine, "rating": r.rating, "price_range": r.price_range,
                "avg_cost_for_two": r.avg_cost_for_two,
                "opening_hours": r.opening_hours, "image_url": r.image_url, "phone": r.phone,
            }
            for r in rows
        ]
    df = load_restaurants_df()
    return df.to_dict(orient="records") if not df.empty else []


def _filter_by_city(data: List[dict], city: str) -> List[dict]:
    """Case-insensitive city filter."""
    city_l = city.lower().strip()
    return [d for d in data if city_l in str(d.get("city", "")).lower()]


def _filter_by_category(data: List[dict], category: str) -> List[dict]:
    cat_l = category.lower().strip()
    return [d for d in data if cat_l in str(d.get("category", "")).lower()]


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@router.post("/itinerary")
async def get_itinerary(
    payload: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full ML pipeline → day-wise itinerary."""
    all_places = _db_places_to_dicts(db)
    all_hotels = _db_hotels_to_dicts(db)
    all_restaurants = _db_restaurants_to_dicts(db)

    city = payload.end_location
    start_city = payload.start_location
    travel_days = payload.travel_days
    total_needed = travel_days * 3  # 3 places per day

    # Groq fallback: destination city not in dataset at all
    city_places = _filter_by_city(all_places, city)
    if not city_places:
        logger.info(f"City '{city}' not in dataset — calling Groq AI...")
        groq_places = await generate_places_for_city(city)
        groq_hotels = await generate_hotels_for_city(city)
        groq_restaurants = await generate_restaurants_for_city(city)
        all_places = groq_places + all_places
        all_hotels = groq_hotels + all_hotels
        all_restaurants = groq_restaurants + all_restaurants
    elif len(city_places) < total_needed:
        # City in CSV but too few places for the trip length — supplement with Groq
        logger.info(f"'{city}' has {len(city_places)} places, need {total_needed} — supplementing via Groq...")
        groq_places = await generate_places_for_city(city)
        groq_hotels = await generate_hotels_for_city(city)
        groq_restaurants = await generate_restaurants_for_city(city)
        existing_names = {p["name"].lower() for p in city_places}
        new_groq = [p for p in groq_places if p["name"].lower() not in existing_names]
        all_places = new_groq + all_places
        all_hotels = groq_hotels + all_hotels
        all_restaurants = groq_restaurants + all_restaurants

    # Also enrich start city if different from destination
    if start_city and start_city.lower().strip() != city.lower().strip():
        start_city_places = _filter_by_city(all_places, start_city)
        if not start_city_places:
            logger.info(f"Start city '{start_city}' not in dataset — fetching via Groq...")
            groq_start = await generate_places_for_city(start_city)
            all_places = groq_start + all_places

    if not all_places:
        raise HTTPException(status_code=503, detail="No place data available")

    itinerary = await generate_itinerary(
        request=payload.model_dump(),
        all_places=all_places,
        all_hotels=all_hotels,
        all_restaurants=all_restaurants,
    )

    try:
        history = UserHistory(
            user_id=current_user.id,
            action="recommended",
            extra_data={
                "destination": payload.end_location,
                "travel_days": payload.travel_days,
                "budget": payload.budget,
            },
        )
        db.add(history)
        db.commit()
    except Exception:
        pass

    return itinerary


@router.get("/places")
async def get_places(
    city: str = Query(None, description="Filter by city name"),
    category: str = Query(None),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """
    Return tourist places.
    Falls back to Groq AI generation if city not found in local data.
    """
    # Step 1: Try DB
    db_rows = db.query(TouristPlace).filter(TouristPlace.is_active == True)  # noqa
    if city:
        db_rows = db_rows.filter(TouristPlace.city.ilike(f"%{city}%"))
    if category:
        db_rows = db_rows.filter(TouristPlace.category.ilike(f"%{category}%"))
    rows = db_rows.order_by(TouristPlace.rating.desc()).limit(limit).all()

    if rows:
        return [
            {
                "id": str(r.id), "name": r.name, "city": r.city,
                "state": r.state, "description": r.description,
                "category": r.category, "rating": r.rating,
                "latitude": r.latitude, "longitude": r.longitude,
                "image_url": r.image_url, "tags": r.tags,
                "entry_fee": r.entry_fee, "is_indoor": r.is_indoor,
                "opening_hours": r.opening_hours,
                "estimated_duration_hours": r.estimated_duration_hours,
                "best_time_to_visit": r.best_time_to_visit,
            }
            for r in rows
        ]

    # Step 2: Try CSV
    df = load_places_df()
    if not df.empty:
        if city:
            df_city = df[df["city"].str.lower().str.contains(city.lower(), na=False)]
        else:
            df_city = df
        if category and not df_city.empty:
            df_city = df_city[df_city["category"].str.lower().str.contains(category.lower(), na=False)]

        if not df_city.empty:
            result = df_city.head(limit).to_dict(orient="records")
            logger.info(f"CSV returned {len(result)} places for city='{city}'")
            return result

    # Step 3: Groq AI fallback — city not found anywhere
    if city:
        logger.info(f"City '{city}' not in CSV — generating via Groq AI...")
        groq_places = await generate_places_for_city(city)
        if groq_places:
            if category:
                groq_places = _filter_by_category(groq_places, category)
            logger.info(f"Groq returned {len(groq_places)} places for {city}")
            return groq_places[:limit]

    # Step 4: Return all CSV places if no city filter
    if not city and not df.empty:
        return df.head(limit).to_dict(orient="records")

    return []


@router.get("/hotels")
async def get_places_hotels(
    city: str = Query(None),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    """Hotels for map overlay — with Groq fallback."""
    rows = db.query(Hotel).filter(Hotel.is_active == True)  # noqa
    if city:
        rows = rows.filter(Hotel.city.ilike(f"%{city}%"))
    db_hotels = rows.limit(limit).all()

    if db_hotels:
        return [{"id": str(h.id), "name": h.name, "city": h.city,
                 "latitude": h.latitude, "longitude": h.longitude,
                 "star_rating": h.star_rating, "price_per_night": h.price_per_night} for h in db_hotels]

    df = load_hotels_df()
    if not df.empty and city:
        df_c = df[df["city"].str.lower().str.contains(city.lower(), na=False)]
        if not df_c.empty:
            return df_c.head(limit).to_dict(orient="records")

    if city:
        return await generate_hotels_for_city(city)

    if not df.empty:
        return df.head(limit).to_dict(orient="records")
    return []


@router.get("/restaurants")
async def get_places_restaurants(
    city: str = Query(None),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    """Restaurants for map overlay — with Groq fallback."""
    rows = db.query(Restaurant).filter(Restaurant.is_active == True)  # noqa
    if city:
        rows = rows.filter(Restaurant.city.ilike(f"%{city}%"))
    db_rests = rows.limit(limit).all()

    if db_rests:
        return [{"id": str(r.id), "name": r.name, "city": r.city,
                 "latitude": r.latitude, "longitude": r.longitude,
                 "cuisine": r.cuisine, "rating": r.rating} for r in db_rests]

    df = load_restaurants_df()
    if not df.empty and city:
        df_c = df[df["city"].str.lower().str.contains(city.lower(), na=False)]
        if not df_c.empty:
            return df_c.head(limit).to_dict(orient="records")

    if city:
        return await generate_restaurants_for_city(city)

    if not df.empty:
        return df.head(limit).to_dict(orient="records")
    return []


@router.get("/similar/{place_id}")
def get_similar_places(place_id: str, top_n: int = 5):
    rec = get_recommender()
    return rec.get_similar_places(place_id, top_n=top_n)
