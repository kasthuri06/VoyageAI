"""
SQLAlchemy ORM models — compatible with both SQLite (dev) and PostgreSQL (prod).
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    DateTime, ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from database.session import Base
import enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class TransportMode(str, enum.Enum):
    car    = "car"
    bike   = "bike"
    walk   = "walk"
    public = "public"
    flight = "flight"


class TripStatus(str, enum.Enum):
    draft     = "draft"
    active    = "active"
    completed = "completed"
    cancelled = "cancelled"


class UserRole(str, enum.Enum):
    user  = "user"
    admin = "admin"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email            = Column(String(255), unique=True, nullable=False, index=True)
    username         = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password  = Column(String(255), nullable=True)
    full_name        = Column(String(200), nullable=True)
    profile_picture  = Column(String(500), nullable=True)
    phone            = Column(String(20),  nullable=True)
    role             = Column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    is_active        = Column(Boolean, default=True)
    is_verified      = Column(Boolean, default=False)
    google_id        = Column(String(200), nullable=True, unique=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trips       = relationship("Trip",           back_populates="user", cascade="all, delete-orphan")
    reviews     = relationship("Review",         back_populates="user", cascade="all, delete-orphan")
    history     = relationship("UserHistory",    back_populates="user", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Tourist Places
# ---------------------------------------------------------------------------
class TouristPlace(Base):
    __tablename__ = "tourist_places"

    id                       = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name                     = Column(String(300), nullable=False, index=True)
    description              = Column(Text,        nullable=True)
    city                     = Column(String(150), nullable=False, index=True)
    state                    = Column(String(150), nullable=True)
    country                  = Column(String(150), nullable=False, default="India")
    latitude                 = Column(Float,       nullable=False)
    longitude                = Column(Float,       nullable=False)
    category                 = Column(String(100), nullable=True, index=True)
    tags                     = Column(JSON,        default=list)
    rating                   = Column(Float,       default=0.0)
    total_reviews            = Column(Integer,     default=0)
    opening_hours            = Column(String(200), nullable=True)
    entry_fee                = Column(Float,       default=0.0)
    image_url                = Column(String(500), nullable=True)
    is_indoor                = Column(Boolean,     default=False)
    estimated_duration_hours = Column(Float,       default=2.0)
    best_time_to_visit       = Column(String(200), nullable=True)
    is_active                = Column(Boolean,     default=True)
    created_at               = Column(DateTime,    default=datetime.utcnow)

    reviews = relationship("Review", back_populates="place", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Hotels
# ---------------------------------------------------------------------------
class Hotel(Base):
    __tablename__ = "hotels"

    id              = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name            = Column(String(300), nullable=False, index=True)
    description     = Column(Text,        nullable=True)
    city            = Column(String(150), nullable=False, index=True)
    address         = Column(String(500), nullable=True)
    latitude        = Column(Float,       nullable=False)
    longitude       = Column(Float,       nullable=False)
    star_rating     = Column(Integer,     default=3)
    user_rating     = Column(Float,       default=0.0)
    price_per_night = Column(Float,       nullable=False)
    amenities       = Column(JSON,        default=list)
    image_url       = Column(String(500), nullable=True)
    phone           = Column(String(30),  nullable=True)
    website         = Column(String(300), nullable=True)
    is_active       = Column(Boolean,     default=True)
    created_at      = Column(DateTime,    default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Restaurants
# ---------------------------------------------------------------------------
class Restaurant(Base):
    __tablename__ = "restaurants"

    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name             = Column(String(300), nullable=False, index=True)
    description      = Column(Text,        nullable=True)
    city             = Column(String(150), nullable=False, index=True)
    address          = Column(String(500), nullable=True)
    latitude         = Column(Float,       nullable=False)
    longitude        = Column(Float,       nullable=False)
    cuisine          = Column(String(200), nullable=True, index=True)
    rating           = Column(Float,       default=0.0)
    price_range      = Column(String(50),  nullable=True)
    avg_cost_for_two = Column(Float,       nullable=True)
    opening_hours    = Column(String(200), nullable=True)
    image_url        = Column(String(500), nullable=True)
    phone            = Column(String(30),  nullable=True)
    is_active        = Column(Boolean,     default=True)
    created_at       = Column(DateTime,    default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------
class Review(Base):
    __tablename__ = "reviews"

    id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id       = Column(String(36), ForeignKey("users.id",         ondelete="CASCADE"), nullable=False)
    place_id      = Column(String(36), ForeignKey("tourist_places.id",ondelete="CASCADE"), nullable=True)
    hotel_id      = Column(String(36), ForeignKey("hotels.id",        ondelete="CASCADE"), nullable=True)
    restaurant_id = Column(String(36), ForeignKey("restaurants.id",   ondelete="CASCADE"), nullable=True)
    rating        = Column(Float,    nullable=False)
    comment       = Column(Text,     nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    user  = relationship("User",         back_populates="reviews")
    place = relationship("TouristPlace", back_populates="reviews")


# ---------------------------------------------------------------------------
# Trips
# ---------------------------------------------------------------------------
class Trip(Base):
    __tablename__ = "trips"

    id             = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id        = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title          = Column(String(300), nullable=False)
    start_location = Column(String(300), nullable=False)
    end_location   = Column(String(300), nullable=False)
    start_date     = Column(DateTime, nullable=True)
    end_date       = Column(DateTime, nullable=True)
    travel_days    = Column(Integer,  default=1)
    budget         = Column(Float,    nullable=True)
    transport_mode = Column(SAEnum(TransportMode), default=TransportMode.car)
    group_size     = Column(Integer,  default=1)
    status         = Column(SAEnum(TripStatus), default=TripStatus.draft)
    itinerary      = Column(JSON,    default=dict)
    total_cost     = Column(Float,   default=0.0)
    is_saved       = Column(Boolean, default=False)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="trips")


# ---------------------------------------------------------------------------
# User Preferences
# ---------------------------------------------------------------------------
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id                    = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id               = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    interests             = Column(JSON,    default=list)
    preferred_transport   = Column(SAEnum(TransportMode), default=TransportMode.car)
    preferred_hotel_rating= Column(Integer, default=3)
    max_budget_per_day    = Column(Float,   nullable=True)
    travel_style          = Column(String(50), nullable=True)
    preferred_cuisine     = Column(JSON,    default=list)
    preferred_travel_time = Column(String(50), nullable=True)
    updated_at            = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")


# ---------------------------------------------------------------------------
# User History
# ---------------------------------------------------------------------------
class UserHistory(Base):
    __tablename__ = "user_history"

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String(36), ForeignKey("users.id",          ondelete="CASCADE"),  nullable=False)
    place_id   = Column(String(36), ForeignKey("tourist_places.id", ondelete="SET NULL"), nullable=True)
    trip_id    = Column(String(36), ForeignKey("trips.id",          ondelete="SET NULL"), nullable=True)
    action      = Column(String(50), nullable=False)
    extra_data  = Column(JSON, default=dict)   # renamed from 'metadata' (reserved by SQLAlchemy)
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="history")
