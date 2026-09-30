"""Admin routes — requires admin role."""
import io
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd

from database.session import get_db
from database.models import User, TouristPlace, Hotel, Restaurant, Trip, Review, UserRole
from core.dependencies import get_admin_user
from ml.datasets import _parse_tags

logger = logging.getLogger(__name__)
router = APIRouter()


def _v(v):
    return v.value if hasattr(v, "value") else v


# ── Analytics ────────────────────────────────────────────────
@router.get("/analytics")
def analytics(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    top_cities = (
        db.query(TouristPlace.city, func.count(TouristPlace.id).label("count"))
        .group_by(TouristPlace.city)
        .order_by(func.count(TouristPlace.id).desc())
        .limit(5).all()
    )
    return {
        "users":       db.query(func.count(User.id)).scalar(),
        "trips":       db.query(func.count(Trip.id)).scalar(),
        "places":      db.query(func.count(TouristPlace.id)).scalar(),
        "hotels":      db.query(func.count(Hotel.id)).scalar(),
        "restaurants": db.query(func.count(Restaurant.id)).scalar(),
        "reviews":     db.query(func.count(Review.id)).scalar(),
        "avg_trip_cost": round(float(db.query(func.avg(Trip.total_cost)).scalar() or 0), 2),
        "top_cities":  [{"city": c, "count": n} for c, n in top_cities],
    }


# ── Users ─────────────────────────────────────────────────────
@router.get("/users")
def list_users(limit: int = Query(50, le=200), db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
    return [
        {"id": str(u.id), "email": u.email, "username": u.username,
         "full_name": u.full_name, "role": _v(u.role),
         "is_active": u.is_active, "created_at": u.created_at.isoformat()}
        for u in users
    ]


@router.put("/users/{user_id}/deactivate")
def deactivate_user(user_id: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"deactivated": True}


@router.put("/users/{user_id}/make-admin")
def make_admin(user_id: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = UserRole.admin
    db.commit()
    return {"role": "admin"}


# ── CSV Uploads ───────────────────────────────────────────────
@router.post("/upload/places")
async def upload_places(file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    df = pd.read_csv(io.StringIO((await file.read()).decode("utf-8")))
    df["tags"] = df["tags"].apply(_parse_tags)
    inserted = 0
    for _, r in df.iterrows():
        db.add(TouristPlace(
            id=str(uuid.uuid4()),
            name=str(r.get("name", "")),
            description=r.get("description"),
            city=str(r.get("city", "")),
            state=r.get("state"),
            country=str(r.get("country", "India")),
            latitude=float(r.get("latitude", 0)),
            longitude=float(r.get("longitude", 0)),
            category=r.get("category"),
            tags=r.get("tags", []),
            rating=float(r.get("rating", 0)),
            entry_fee=float(r.get("entry_fee", 0)),
            opening_hours=r.get("opening_hours"),
            is_indoor=str(r.get("is_indoor", "false")).lower() == "true",
            estimated_duration_hours=float(r.get("estimated_duration_hours", 2)),
            best_time_to_visit=r.get("best_time_to_visit"),
            image_url=r.get("image_url"),
        ))
        inserted += 1
    db.commit()
    return {"inserted": inserted}


@router.post("/upload/hotels")
async def upload_hotels(file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    df = pd.read_csv(io.StringIO((await file.read()).decode("utf-8")))
    df["amenities"] = df["amenities"].apply(_parse_tags)
    inserted = 0
    for _, r in df.iterrows():
        db.add(Hotel(
            id=str(uuid.uuid4()),
            name=str(r.get("name", "")),
            description=r.get("description"),
            city=str(r.get("city", "")),
            address=r.get("address"),
            latitude=float(r.get("latitude", 0)),
            longitude=float(r.get("longitude", 0)),
            star_rating=int(r.get("star_rating", 3)),
            user_rating=float(r.get("user_rating", 0)),
            price_per_night=float(r.get("price_per_night", 0)),
            amenities=r.get("amenities", []),
            image_url=r.get("image_url"),
            phone=r.get("phone"),
            website=r.get("website"),
        ))
        inserted += 1
    db.commit()
    return {"inserted": inserted}


@router.post("/upload/restaurants")
async def upload_restaurants(file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    df = pd.read_csv(io.StringIO((await file.read()).decode("utf-8")))
    inserted = 0
    for _, r in df.iterrows():
        db.add(Restaurant(
            id=str(uuid.uuid4()),
            name=str(r.get("name", "")),
            description=r.get("description"),
            city=str(r.get("city", "")),
            address=r.get("address"),
            latitude=float(r.get("latitude", 0)),
            longitude=float(r.get("longitude", 0)),
            cuisine=r.get("cuisine"),
            rating=float(r.get("rating", 0)),
            price_range=r.get("price_range"),
            avg_cost_for_two=float(r.get("avg_cost_for_two", 0)) if r.get("avg_cost_for_two") else None,
            opening_hours=r.get("opening_hours"),
            image_url=r.get("image_url"),
            phone=r.get("phone"),
        ))
        inserted += 1
    db.commit()
    return {"inserted": inserted}


@router.delete("/places/{place_id}")
def delete_place(place_id: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    place = db.query(TouristPlace).filter(TouristPlace.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    place.is_active = False
    db.commit()
    return {"deleted": True}
