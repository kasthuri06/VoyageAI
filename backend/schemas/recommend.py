"""Recommendation schemas — UUID-agnostic."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class RecommendationRequest(BaseModel):
    start_location: str = Field(..., example="Mumbai")
    end_location: str = Field(..., example="Goa")
    travel_days: int = Field(..., ge=1, le=30, example=3)
    budget: float = Field(..., gt=0, example=15000.0)
    transport_mode: str = Field("car", example="car")
    interests: List[str] = Field(..., example=["beach", "nature", "food"])
    group_size: int = Field(1, ge=1, example=2)
    preferred_hotel_rating: int = Field(3, ge=1, le=5)
    travel_style: Optional[str] = Field(None, example="couple")
    preferred_travel_time: Optional[str] = Field(None, example="morning")


class PlaceOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    city: str
    latitude: float
    longitude: float
    category: Optional[str] = None
    tags: List[str] = []
    rating: float
    entry_fee: float
    opening_hours: Optional[str] = None
    estimated_duration_hours: float
    image_url: Optional[str] = None
    is_indoor: bool
    similarity_score: Optional[float] = None

    model_config = {"from_attributes": True}


class ItinerarySlot(BaseModel):
    time_slot: str
    place: Optional[PlaceOut] = None
    hotel: Optional[Dict[str, Any]] = None
    restaurant: Optional[Dict[str, Any]] = None
    travel_time_minutes: Optional[float] = None
    notes: Optional[str] = None


class DayPlan(BaseModel):
    day: int
    date: Optional[str] = None
    slots: List[ItinerarySlot]
    estimated_cost: float
    weather: Optional[Dict[str, Any]] = None


class ItineraryResponse(BaseModel):
    trip_id: Optional[str] = None
    title: str
    start_location: str
    end_location: str
    travel_days: int
    total_budget: float
    estimated_total_cost: float
    transport_mode: str
    group_size: int
    days: List[DayPlan]
    recommended_hotels: List[Dict[str, Any]]
    top_places: List[PlaceOut]
    weather_summary: Optional[Dict[str, Any]] = None
    route_summary: Optional[Dict[str, Any]] = None
