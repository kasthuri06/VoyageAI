"""Trip schemas — UUID-agnostic (works with SQLite strings and PostgreSQL UUIDs)."""
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
from datetime import datetime


class TripCreate(BaseModel):
    title: str
    start_location: str
    end_location: str
    travel_days: int
    budget: Optional[float] = None
    transport_mode: Optional[str] = "car"
    group_size: Optional[int] = 1
    itinerary: Optional[Dict[str, Any]] = None


class TripOut(BaseModel):
    id: str
    title: str
    start_location: str
    end_location: str
    travel_days: int
    budget: Optional[float] = None
    transport_mode: Optional[str] = None
    group_size: Optional[int] = None
    status: str
    itinerary: Optional[Dict[str, Any]] = None
    total_cost: float
    is_saved: bool
    created_at: datetime

    @field_validator("status", mode="before")
    @classmethod
    def coerce_status(cls, v):
        return v.value if hasattr(v, "value") else v

    @field_validator("transport_mode", mode="before")
    @classmethod
    def coerce_transport(cls, v):
        return v.value if hasattr(v, "value") else v

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    place_id: Optional[str] = None
    hotel_id: Optional[str] = None
    restaurant_id: Optional[str] = None
    rating: float
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: str
    rating: float
    comment: Optional[str] = None
    created_at: datetime
    username: Optional[str] = None

    model_config = {"from_attributes": True}
