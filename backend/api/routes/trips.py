"""
Trip management routes: /trips
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import Trip, TripStatus, User
from schemas.trip import TripCreate, TripOut
from core.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=TripOut, status_code=201)
def create_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a new trip."""
    trip = Trip(
        user_id=str(current_user.id),
        title=payload.title,
        start_location=payload.start_location,
        end_location=payload.end_location,
        travel_days=payload.travel_days,
        budget=payload.budget,
        transport_mode=payload.transport_mode,
        group_size=payload.group_size,
        itinerary=payload.itinerary or {},
        is_saved=True,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/")
def list_trips(
    status: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all trips for the current user."""
    query = db.query(Trip).filter(Trip.user_id == str(current_user.id))
    if status:
        query = query.filter(Trip.status == status)
    trips = query.order_by(Trip.created_at.desc()).limit(limit).all()
    return [
        {
            "id": str(t.id), "title": t.title,
            "start_location": t.start_location, "end_location": t.end_location,
            "travel_days": t.travel_days,
            "status": t.status.value if hasattr(t.status, "value") else t.status,
            "total_cost": t.total_cost, "is_saved": t.is_saved,
            "created_at": t.created_at.isoformat(),
        }
        for t in trips
    ]


@router.get("/{trip_id}")
def get_trip(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full details of a specific trip including itinerary."""
    trip = db.query(Trip).filter(
        Trip.id == trip_id,
        Trip.user_id == str(current_user.id),
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {
        "id": str(trip.id), "title": trip.title,
        "start_location": trip.start_location, "end_location": trip.end_location,
        "travel_days": trip.travel_days, "budget": trip.budget,
        "transport_mode": trip.transport_mode.value if hasattr(trip.transport_mode, "value") else trip.transport_mode,
        "group_size": trip.group_size,
        "status": trip.status.value if hasattr(trip.status, "value") else trip.status,
        "itinerary": trip.itinerary, "total_cost": trip.total_cost,
        "is_saved": trip.is_saved, "created_at": trip.created_at.isoformat(),
    }


@router.put("/{trip_id}/save")
def toggle_save(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle saved status of a trip."""
    trip = db.query(Trip).filter(
        Trip.id == trip_id,
        Trip.user_id == str(current_user.id),
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip.is_saved = not trip.is_saved
    db.commit()
    return {"is_saved": trip.is_saved}


@router.put("/{trip_id}/status")
def update_status(
    trip_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update trip status."""
    valid = {s.value for s in TripStatus}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid}")
    trip = db.query(Trip).filter(
        Trip.id == trip_id,
        Trip.user_id == str(current_user.id),
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip.status = status
    db.commit()
    return {"status": status}


@router.delete("/{trip_id}", status_code=204)
def delete_trip(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a trip."""
    trip = db.query(Trip).filter(
        Trip.id == trip_id,
        Trip.user_id == str(current_user.id),
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
