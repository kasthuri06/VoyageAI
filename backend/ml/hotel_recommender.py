"""
Voyage AI – Hotel Recommendation Service

Recommends hotels based on:
  - Budget (price_per_night)
  - Distance from current location
  - Star rating preference
  - User rating
  - Required amenities
"""
import logging
from typing import List, Dict, Any, Optional

from geopy.distance import geodesic

logger = logging.getLogger(__name__)

# Speed factor: average hotel search radius in km
DEFAULT_RADIUS_KM = 15.0


def recommend_hotels(
    hotels: List[Dict[str, Any]],
    budget_per_night: float,
    latitude: float,
    longitude: float,
    min_star_rating: int = 3,
    required_amenities: Optional[List[str]] = None,
    top_n: int = 5,
    radius_km: float = DEFAULT_RADIUS_KM,
) -> List[Dict[str, Any]]:
    """
    Filter and score hotels based on user preferences.

    Scoring formula:
        score = 0.4 * budget_score + 0.3 * rating_score + 0.2 * distance_score + 0.1 * amenity_score

    Args:
        hotels:            List of hotel dicts (from DB or CSV)
        budget_per_night:  Maximum budget per night
        latitude:          User's current / city center latitude
        longitude:         User's current / city center longitude
        min_star_rating:   Minimum star rating (1-5)
        required_amenities: List of must-have amenities (e.g. ["wifi","pool"])
        top_n:             Number of recommendations to return
        radius_km:         Search radius

    Returns:
        Top N scored hotels sorted by recommendation_score descending.
    """
    if not hotels:
        return []

    scored = []

    for hotel in hotels:
        # 1. Budget filter
        price = float(hotel.get("price_per_night", 0))
        if price > budget_per_night * 1.2:  # allow 20% overage
            continue

        # 2. Star rating filter
        stars = int(hotel.get("star_rating", 3))
        if stars < min_star_rating - 1:  # allow 1 star leniency
            continue

        # 3. Distance filter
        try:
            dist_km = geodesic(
                (latitude, longitude),
                (float(hotel["latitude"]), float(hotel["longitude"])),
            ).km
        except Exception:
            dist_km = 0.0

        if dist_km > radius_km:
            continue

        # --- Scoring ---

        # Budget score: closer to budget ceiling → higher score
        if budget_per_night > 0:
            budget_score = min(price / budget_per_night, 1.0)
        else:
            budget_score = 0.5

        # Rating score: user_rating / 5
        user_rating = float(hotel.get("user_rating", 3.0))
        rating_score = user_rating / 5.0

        # Distance score: 1 = very close, 0 = at radius boundary
        distance_score = max(0.0, 1.0 - (dist_km / radius_km))

        # Amenity score
        amenity_score = 0.0
        if required_amenities:
            hotel_amenities = hotel.get("amenities", [])
            if isinstance(hotel_amenities, str):
                import json
                try:
                    hotel_amenities = json.loads(hotel_amenities.replace("'", '"'))
                except Exception:
                    hotel_amenities = []
            hotel_amenities_lower = [a.lower() for a in hotel_amenities]
            matched = sum(1 for a in required_amenities if a.lower() in hotel_amenities_lower)
            amenity_score = matched / len(required_amenities)
        else:
            amenity_score = 0.5

        # Composite score
        composite = (
            0.35 * budget_score
            + 0.35 * rating_score
            + 0.20 * distance_score
            + 0.10 * amenity_score
        )

        scored.append({
            **hotel,
            "distance_km": round(dist_km, 2),
            "recommendation_score": round(composite, 4),
        })

    # Sort by composite score descending
    scored.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return scored[:top_n]


def recommend_nearby_hotels(
    hotels: List[Dict[str, Any]],
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    top_n: int = 3,
) -> List[Dict[str, Any]]:
    """Return the closest hotels within a radius, sorted by distance."""
    result = []
    for hotel in hotels:
        try:
            dist = geodesic(
                (latitude, longitude),
                (float(hotel["latitude"]), float(hotel["longitude"])),
            ).km
        except Exception:
            dist = 999.0

        if dist <= radius_km:
            result.append({**hotel, "distance_km": round(dist, 2)})

    result.sort(key=lambda x: x["distance_km"])
    return result[:top_n]
