"""User-related schemas — UUID-agnostic (works with SQLite strings and PostgreSQL UUIDs)."""
from pydantic import BaseModel, EmailStr
from typing import List, Optional


class UserOut(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None


class PreferenceUpdate(BaseModel):
    interests: Optional[List[str]] = None
    preferred_transport: Optional[str] = None
    preferred_hotel_rating: Optional[int] = None
    max_budget_per_day: Optional[float] = None
    travel_style: Optional[str] = None
    preferred_cuisine: Optional[List[str]] = None
    preferred_travel_time: Optional[str] = None


class PreferenceOut(BaseModel):
    interests: List[str] = []
    preferred_transport: Optional[str] = None
    preferred_hotel_rating: Optional[int] = 3
    max_budget_per_day: Optional[float] = None
    travel_style: Optional[str] = None
    preferred_cuisine: List[str] = []
    preferred_travel_time: Optional[str] = None

    model_config = {"from_attributes": True}
