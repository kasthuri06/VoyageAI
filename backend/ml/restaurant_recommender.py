"""
Voyage AI – Restaurant Recommendation Service

Recommends restaurants based on:
  - Proximity (distance from current location)
  - Cuisine preferences
  - Budget (avg_cost_for_two)
  - User ratings
"""
import json
import logging
from typing import List, Dict, Any, Optional

from geopy.distance import geodesic

logger = logging.getLogger(__name__)


def recommend_restaurants(
    restaurants: List[Dict[str, Any]],
    latitude: float,
    longitude: float,
    budget_for_two: Optional[float] = None,
    preferred_cuisines: Optional[List[str]] = None,
    min_rating: float = 3.5,
    top_n: int = 5,
    radius_km: float = 3.0,
) -> List[Dict[str, Any]]:
    """
    Filter and score restaurants for recommendation.

    Scoring:
        score = 0.4 * rating_score + 0.35 * proximity_score + 0.15 * budget_score + 0.10 * cuisine_score

    Args:
        restaurants:        Full restaurant list
        latitude:           Reference latitude
        longitude:          Reference longitude
        budget_for_two:     Max budget for two people
        preferred_cuisines: e.g. ["North Indian", "Italian"]
        min_rating:         Minimum acceptable rating
        top_n:              Number of results
        radius_km:          Search radius

    Returns:
        Top N restaurants sorted by recommendation_score.
    """
    if not restaurants:
        return []

    scored = []

    for r in restaurants:
        # Distance filter
        try:
            dist = geodesic(
                (latitude, longitude),
                (float(r["latitude"]), float(r["longitude"])),
            ).km
        except Exception:
            dist = 999.0

        if dist > radius_km:
            continue

        # Rating filter
        rating = float(r.get("rating", 0))
        if rating < min_rating - 0.5:  # slight leniency
            continue

        # Budget filter
        avg_cost = r.get("avg_cost_for_two")
        if avg_cost and budget_for_two:
            avg_cost = float(avg_cost)
            if avg_cost > budget_for_two * 1.3:
                continue

        # --- Scoring ---
        proximity_score = max(0.0, 1.0 - (dist / radius_km))
        rating_score = min(rating / 5.0, 1.0)

        budget_score = 0.5
        if budget_for_two and avg_cost:
            budget_score = min(float(avg_cost) / budget_for_two, 1.0)

        cuisine_score = 0.0
        if preferred_cuisines:
            r_cuisine = str(r.get("cuisine", "")).lower()
            matches = any(c.lower() in r_cuisine for c in preferred_cuisines)
            cuisine_score = 1.0 if matches else 0.0
        else:
            cuisine_score = 0.5

        composite = (
            0.40 * rating_score
            + 0.35 * proximity_score
            + 0.15 * budget_score
            + 0.10 * cuisine_score
        )

        scored.append({
            **r,
            "distance_km": round(dist, 2),
            "recommendation_score": round(composite, 4),
        })

    scored.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return scored[:top_n]


def get_nearby_restaurants(
    restaurants: List[Dict[str, Any]],
    latitude: float,
    longitude: float,
    radius_km: float = 1.5,
    top_n: int = 3,
) -> List[Dict[str, Any]]:
    """Return the closest restaurants sorted by distance."""
    result = []
    for r in restaurants:
        try:
            dist = geodesic(
                (latitude, longitude),
                (float(r["latitude"]), float(r["longitude"])),
            ).km
        except Exception:
            dist = 999.0

        if dist <= radius_km:
            result.append({**r, "distance_km": round(dist, 2)})

    result.sort(key=lambda x: x["distance_km"])
    return result[:top_n]
