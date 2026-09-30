"""
User routes: /user/profile, /user/preferences, /user/saved-trips
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, UserPreference, Trip
from schemas.user import UserOut, UserUpdate, PreferenceOut, PreferenceUpdate
from core.dependencies import get_current_user

router = APIRouter()


def _enum_val(v):
    """Safely get .value from enum or return string as-is."""
    return v.value if hasattr(v, "value") else v


@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserOut)
def update_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.phone is not None:
        current_user.phone = payload.phone
    if payload.profile_picture is not None:
        current_user.profile_picture = payload.profile_picture
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/preferences", response_model=PreferenceOut)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prefs = db.query(UserPreference).filter(
        UserPreference.user_id == str(current_user.id)
    ).first()
    if not prefs:
        prefs = UserPreference(user_id=str(current_user.id))
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.put("/preferences", response_model=PreferenceOut)
def update_preferences(
    payload: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prefs = db.query(UserPreference).filter(
        UserPreference.user_id == str(current_user.id)
    ).first()
    if not prefs:
        prefs = UserPreference(user_id=str(current_user.id))
        db.add(prefs)
        db.flush()

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prefs, field, value)

    db.commit()
    db.refresh(prefs)
    return prefs


@router.get("/saved-trips")
def get_saved_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trips = (
        db.query(Trip)
        .filter(
            Trip.user_id == str(current_user.id),
            Trip.is_saved == True,  # noqa: E712
        )
        .order_by(Trip.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(t.id),
            "title": t.title,
            "start_location": t.start_location,
            "end_location": t.end_location,
            "travel_days": t.travel_days,
            "status": _enum_val(t.status),
            "total_cost": t.total_cost,
            "created_at": t.created_at.isoformat(),
        }
        for t in trips
    ]


@router.get("/favorite-places")
def get_favorite_places(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from database.models import UserHistory
    favorites = (
        db.query(UserHistory)
        .filter(
            UserHistory.user_id == str(current_user.id),
            UserHistory.action == "saved",
        )
        .order_by(UserHistory.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "history_id": str(h.id),
            "place_id": str(h.place_id) if h.place_id else None,
            "saved_at": h.created_at.isoformat(),
        }
        for h in favorites
    ]
