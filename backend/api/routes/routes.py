"""
Route optimization API: /routes/optimize, /routes/directions
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ml.route_optimizer import optimize_route, get_google_route, get_ors_route, _algorithm_fallback

router = APIRouter()


class PlaceCoord(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    latitude: float
    longitude: float


class RouteRequest(BaseModel):
    places: List[PlaceCoord]
    transport_mode: str = "car"
    mode: Optional[str] = None  # override: "algorithm" | "google" | "ors"


class DirectionsRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    transport_mode: str = "car"
    routing_source: str = "algorithm"  # "algorithm" | "google" | "ors"


@router.post("/optimize")
async def optimize(payload: RouteRequest):
    """
    Optimize visitation order for a list of places and return route details.
    Uses Dijkstra / A* algorithm or external APIs based on config.
    """
    if len(payload.places) < 2:
        raise HTTPException(status_code=400, detail="At least 2 places required")
    if len(payload.places) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 places per request")

    places_dicts = [p.model_dump() for p in payload.places]
    result = await optimize_route(places_dicts, payload.transport_mode)
    return result


@router.post("/directions")
async def get_directions(payload: DirectionsRequest):
    """
    Get turn-by-turn directions between two coordinates.
    Supports Google Maps API, OpenRouteService, or built-in algorithm.
    """
    origin = (payload.origin_lat, payload.origin_lon)
    dest = (payload.dest_lat, payload.dest_lon)

    if payload.routing_source == "google":
        mode_map = {"car": "driving", "bike": "bicycling", "walk": "walking", "public": "transit"}
        result = await get_google_route(origin, dest, mode=mode_map.get(payload.transport_mode, "driving"))
    elif payload.routing_source == "ors":
        profile_map = {"car": "driving-car", "bike": "cycling-regular", "walk": "foot-walking"}
        result = await get_ors_route(origin, dest, profile=profile_map.get(payload.transport_mode, "driving-car"))
    else:
        result = _algorithm_fallback(origin, dest)

    return result
