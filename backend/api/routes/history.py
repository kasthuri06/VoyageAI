"""
User history routes: /history
"""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import UserHistory, User
from core.dependencies import get_current_user

router = APIRouter()


@router.get("/")
def get_history(
    action: str = Query(None),
    limit: int = Query(30, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return user activity history."""
    query = db.query(UserHistory).filter(UserHistory.user_id == str(current_user.id))
    if action:
        query = query.filter(UserHistory.action == action)
    items = query.order_by(UserHistory.created_at.desc()).limit(limit).all()
    return [
        {
            "id": str(h.id),
            "action": h.action,
            "place_id": str(h.place_id) if h.place_id else None,
            "trip_id": str(h.trip_id) if h.trip_id else None,
            "metadata": h.extra_data,
            "created_at": h.created_at.isoformat(),
        }
        for h in items
    ]


@router.post("/log")
def log_action(
    place_id: str = None,
    trip_id: str = None,
    action: str = "viewed",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a user action."""
    history = UserHistory(
        user_id=str(current_user.id),
        place_id=place_id,
        trip_id=trip_id,
        action=action,
    )
    db.add(history)
    db.commit()
    return {"logged": True}
