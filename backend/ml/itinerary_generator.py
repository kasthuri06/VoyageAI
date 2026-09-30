"""
Voyage AI – Intelligent Day-wise Itinerary Generator

ML Prediction Flow:
  User Input → Feature Engineering → Recommendation Model → Top Attractions
  → Route Optimization → Weather Filtering → Hotel Recommendation
  → Restaurant Recommendation → Generate Final Itinerary

Generates:
  Day 1 → Morning / Afternoon / Evening / Night
  Day 2 …
  Day N …

Each slot includes:
  - Place / Hotel / Restaurant
  - Travel time
  - Opening hours
  - Estimated cost
  - Nearby suggestions
"""
import logging
import math
from datetime import date, timedelta
from typing import List, Dict, Any, Optional

from ml.recommendation_engine import get_recommender
from ml.route_optimizer import optimize_route, nearest_neighbour_tsp
from ml.weather_service import get_weather_forecast
from ml.hotel_recommender import recommend_hotels
from ml.restaurant_recommender import recommend_restaurants, get_nearby_restaurants

logger = logging.getLogger(__name__)

# Time slot definitions (approximate hours in a day)
TIME_SLOTS = ["morning", "afternoon", "evening", "night"]
SLOT_TIMES = {
    "morning":   "08:00 – 11:30",
    "afternoon": "12:00 – 15:30",
    "evening":   "16:00 – 19:30",
    "night":     "20:00 – 22:00",
}

# Average places per day that fit comfortably
PLACES_PER_DAY = 3  # morning, afternoon, evening (night = hotel/dinner)


async def generate_itinerary(
    request: Dict[str, Any],
    all_places: List[Dict],
    all_hotels: List[Dict],
    all_restaurants: List[Dict],
) -> Dict[str, Any]:
    """
    Full itinerary generation pipeline.

    Args:
        request: Parsed recommendation request dict
        all_places: All tourist places from DB/CSV
        all_hotels: All hotels from DB/CSV
        all_restaurants: All restaurants from DB/CSV

    Returns:
        Complete itinerary dict compatible with ItineraryResponse schema
    """
    interests = request.get("interests", [])
    travel_days = int(request.get("travel_days", 3))
    budget = float(request.get("budget", 10000))
    transport_mode = request.get("transport_mode", "car")
    group_size = int(request.get("group_size", 1))
    city = request.get("end_location", request.get("start_location", ""))
    min_hotel_stars = int(request.get("preferred_hotel_rating", 3))
    travel_style = request.get("travel_style", "solo")
    preferred_travel_time = request.get("preferred_travel_time", "morning")

    # ------------------------------------------------------------------
    # Step 1: Fetch weather forecast
    # ------------------------------------------------------------------
    forecast_data = await get_weather_forecast(city, days=travel_days)
    daily_forecasts = forecast_data.get("forecast", [])
    weather_summary = {
        "city": city,
        "avg_rain_probability": sum(d.get("rain_probability", 0) for d in daily_forecasts) / max(len(daily_forecasts), 1),
        "days": daily_forecasts,
    }

    # ------------------------------------------------------------------
    # Step 2: Build the full candidate pool and get recommendations
    # ------------------------------------------------------------------
    recommender = get_recommender()
    total_places_needed = travel_days * PLACES_PER_DAY  # one unique place per slot

    city_lower = city.lower().strip()
    start_city_lower = request.get("start_location", "").lower().strip()

    # Build city-specific pool from all_places (CSV + Groq) — destination city only
    city_pool = [
        p for p in all_places
        if city_lower in str(p.get("city", "")).lower()
        or city_lower in str(p.get("state", "")).lower()
    ]

    # Also include start location places if different from destination
    if start_city_lower and start_city_lower != city_lower:
        start_pool = [
            p for p in all_places
            if start_city_lower in str(p.get("city", "")).lower()
            or start_city_lower in str(p.get("state", "")).lower()
        ]
        city_pool = city_pool + start_pool

    # ML recommendations filtered to destination city
    recommended = recommender.recommend(
        interests=interests,
        city=city,
        top_n=total_places_needed,
        weather_is_bad=weather_summary["avg_rain_probability"] > 0.5,
    )

    # Merge city_pool into recommendations — deduplicated, ML results first
    seen_ids: set = {str(p.get("id", "")) for p in recommended}
    for p in city_pool:
        pid = str(p.get("id", ""))
        if pid not in seen_ids:
            recommended.append(p)
            seen_ids.add(pid)

    # If still not enough, repeat the available city places in a different order
    # rather than pulling unrelated cities — better to have fewer places than wrong ones
    if len(recommended) < total_places_needed and len(recommended) > 0:
        logger.info(
            f"[Itinerary] Only {len(recommended)} unique places found for '{city}' "
            f"(need {total_places_needed}). Using available places — some days may have free time."
        )

    unique_places = recommended[:total_places_needed]
    logger.info(f"[Itinerary] {city}: {len(unique_places)} unique places for "
                f"{travel_days} days ({total_places_needed} slots needed)")

    # ------------------------------------------------------------------
    # Step 3: Route optimization — order the places efficiently
    # ------------------------------------------------------------------
    if len(unique_places) > 1:
        try:
            route_result = await optimize_route(unique_places[:min(len(unique_places), 20)], transport_mode)
            ordered_places = route_result["ordered_places"]
            route_summary = {
                "total_distance_km": route_result["total_distance_km"],
                "total_duration_minutes": route_result["total_duration_minutes"],
                "routing_source": route_result["legs"][0]["source"] if route_result["legs"] else "algorithm",
            }
        except Exception as e:
            logger.warning(f"Route optimization failed: {e}. Using default order.")
            ordered_places = unique_places
            route_summary = {"total_distance_km": 0, "total_duration_minutes": 0, "routing_source": "none"}
    else:
        ordered_places = unique_places
        route_summary = {}

    # Pre-build per-day place assignments.
    # Strategy:
    #   - Assign unique places across ALL days first (no repeats at all if pool is big enough)
    #   - If pool has fewer places than total slots, first distribute evenly so each day
    #     gets different places, then fill remaining slots with "free time"
    #   - NEVER assign the same place twice on the same day
    pool = ordered_places
    pool_size = len(pool)
    day_place_map: List[List[Dict]] = []

    if pool_size == 0:
        for _ in range(travel_days):
            day_place_map.append([])
    else:
        # Assign places sequentially across all days, never repeating on the same day
        # cursor moves forward globally — each place is used at most once unless
        # pool is smaller than total_slots, in which case remaining slots stay empty
        total_slots = travel_days * PLACES_PER_DAY
        # Build a flat assignment list — only use each place once
        assignment = pool[:total_slots]  # may be shorter than total_slots if pool is small

        cursor = 0
        for day_idx in range(travel_days):
            day_places = []
            for _ in range(PLACES_PER_DAY):
                if cursor < len(assignment):
                    day_places.append(assignment[cursor])
                    cursor += 1
                # else: slot stays empty → "Free time" in the UI
            day_place_map.append(day_places)

    top_places = pool  # keep for response metadata

    # ------------------------------------------------------------------
    # Step 4: Hotel recommendation
    # ------------------------------------------------------------------
    # Find approximate city center coordinates
    city_lat, city_lon = _get_city_center(all_places, city)
    budget_per_night = budget / travel_days * 0.30  # ~30% of daily budget on hotel

    recommended_hotels = recommend_hotels(
        hotels=all_hotels,
        budget_per_night=budget_per_night,
        latitude=city_lat,
        longitude=city_lon,
        min_star_rating=min_hotel_stars,
        top_n=5,
    )

    # ------------------------------------------------------------------
    # Step 5: Build day-wise itinerary
    # ------------------------------------------------------------------
    days = []
    today = date.today()

    # Estimate per-day budget split
    hotel_cost_per_night = recommended_hotels[0]["price_per_night"] if recommended_hotels else budget_per_night
    daily_budget = budget / travel_days
    food_budget_per_day = daily_budget * 0.20
    activities_budget_per_day = daily_budget * 0.25

    for day_num in range(1, travel_days + 1):
        day_date = today + timedelta(days=day_num - 1)
        day_forecast = daily_forecasts[day_num - 1] if day_num - 1 < len(daily_forecasts) else {}
        is_bad_weather = day_forecast.get("is_bad_weather", False)

        slots = []
        day_cost = hotel_cost_per_night
        today_places = day_place_map[day_num - 1]  # pre-assigned unique places for this day

        for slot_idx, slot_name in enumerate(["morning", "afternoon", "evening"]):
            if slot_idx < len(today_places):
                place = today_places[slot_idx]

                # Weather check: prefer indoor on bad-weather days
                if is_bad_weather and not place.get("is_indoor", False):
                    indoor_alternatives = [
                        p for p in today_places[slot_idx:]
                        if p.get("is_indoor", False)
                    ]
                    if indoor_alternatives:
                        place = indoor_alternatives[0]

                place_lat = float(place.get("latitude", city_lat))
                place_lon = float(place.get("longitude", city_lon))

                nearby_restaurants = get_nearby_restaurants(
                    all_restaurants, place_lat, place_lon, radius_km=2.0, top_n=2
                )

                prev_place = today_places[slot_idx - 1] if slot_idx > 0 else None
                travel_time = _estimate_travel_time(prev_place, place, transport_mode)

                entry_fee = float(place.get("entry_fee", 0)) * group_size
                day_cost += entry_fee

                slots.append({
                    "time_slot": slot_name,
                    "time_range": SLOT_TIMES[slot_name],
                    "place": _serialize_place(place),
                    "travel_time_minutes": travel_time,
                    "notes": _generate_slot_notes(place, slot_name, day_forecast),
                    "nearby_restaurants": nearby_restaurants[:2],
                })
            else:
                # Genuinely no more places — mark as free time
                slots.append({
                    "time_slot": slot_name,
                    "time_range": SLOT_TIMES[slot_name],
                    "place": None,
                    "notes": "Free time / leisure",
                    "travel_time_minutes": 0,
                    "nearby_restaurants": [],
                })

        # Night slot → hotel + dinner
        hotel_for_night = recommended_hotels[0] if recommended_hotels else None
        night_restaurants = recommend_restaurants(
            all_restaurants,
            city_lat, city_lon,
            budget_for_two=food_budget_per_day * 2,
            preferred_cuisines=request.get("preferred_cuisines", []),
            top_n=2,
        )
        day_cost += food_budget_per_day

        slots.append({
            "time_slot": "night",
            "time_range": SLOT_TIMES["night"],
            "hotel": _serialize_hotel(hotel_for_night) if hotel_for_night else None,
            "restaurant": _serialize_restaurant(night_restaurants[0]) if night_restaurants else None,
            "notes": "Check into hotel and enjoy dinner",
            "travel_time_minutes": 0,
            "nearby_restaurants": night_restaurants,
        })

        days.append({
            "day": day_num,
            "date": day_date.isoformat(),
            "slots": slots,
            "estimated_cost": round(day_cost, 2),
            "weather": day_forecast,
        })

    estimated_total = sum(d["estimated_cost"] for d in days)

    return {
        "title": f"{travel_days}-Day Trip to {city}",
        "start_location": request.get("start_location", city),
        "end_location": city,
        "travel_days": travel_days,
        "total_budget": budget,
        "estimated_total_cost": round(estimated_total, 2),
        "transport_mode": transport_mode,
        "group_size": group_size,
        "days": days,
        "recommended_hotels": [_serialize_hotel(h) for h in recommended_hotels],
        "top_places": [_serialize_place(p) for p in top_places[:10]],
        "weather_summary": weather_summary,
        "route_summary": route_summary,
    }


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_city_center(places: List[Dict], city: str) -> tuple:
    """Estimate city center from known places."""
    city_places = [p for p in places if city.lower() in str(p.get("city", "")).lower()]
    if city_places:
        lat = sum(float(p.get("latitude", 0)) for p in city_places) / len(city_places)
        lon = sum(float(p.get("longitude", 0)) for p in city_places) / len(city_places)
        return lat, lon
    # Default fallback: center of India
    return 20.5937, 78.9629


def _estimate_travel_time(
    from_place: Optional[Dict],
    to_place: Dict,
    transport_mode: str,
) -> float:
    """Estimate travel time in minutes between two places."""
    if not from_place:
        return 15.0

    from geopy.distance import geodesic
    try:
        dist_km = geodesic(
            (float(from_place["latitude"]), float(from_place["longitude"])),
            (float(to_place["latitude"]), float(to_place["longitude"])),
        ).km
    except Exception:
        return 20.0

    speed_map = {"car": 40, "bike": 25, "walk": 5, "public": 30, "flight": 500}
    speed = speed_map.get(transport_mode, 40)
    return round((dist_km / speed) * 60, 1)


def _generate_slot_notes(place: Dict, slot: str, weather: Dict) -> str:
    """Generate contextual notes for a time slot."""
    notes = []
    if place.get("opening_hours"):
        notes.append(f"Open: {place['opening_hours']}")
    if place.get("estimated_duration_hours"):
        notes.append(f"Duration: ~{place['estimated_duration_hours']}h")
    if weather.get("is_bad_weather"):
        notes.append("⚠️ Rain expected – carry an umbrella")
    if place.get("best_time_to_visit"):
        notes.append(f"Best time: {place['best_time_to_visit']}")
    return " | ".join(notes) if notes else ""


def _serialize_place(place: Dict) -> Dict:
    return {
        "id": str(place.get("id", "")),
        "name": place.get("name", ""),
        "description": place.get("description", ""),
        "city": place.get("city", ""),
        "latitude": place.get("latitude"),
        "longitude": place.get("longitude"),
        "category": place.get("category", ""),
        "tags": place.get("tags", []),
        "rating": place.get("rating", 0),
        "entry_fee": place.get("entry_fee", 0),
        "opening_hours": place.get("opening_hours"),
        "estimated_duration_hours": place.get("estimated_duration_hours", 2),
        "image_url": place.get("image_url"),
        "is_indoor": place.get("is_indoor", False),
        "similarity_score": place.get("similarity_score"),
    }


def _serialize_hotel(hotel: Dict) -> Dict:
    return {
        "id": str(hotel.get("id", "")),
        "name": hotel.get("name", ""),
        "city": hotel.get("city", ""),
        "address": hotel.get("address", ""),
        "latitude": hotel.get("latitude"),
        "longitude": hotel.get("longitude"),
        "star_rating": hotel.get("star_rating", 3),
        "user_rating": hotel.get("user_rating", 0),
        "price_per_night": hotel.get("price_per_night", 0),
        "amenities": hotel.get("amenities", []),
        "image_url": hotel.get("image_url"),
        "phone": hotel.get("phone"),
        "website": hotel.get("website"),
        "distance_km": hotel.get("distance_km"),
        "recommendation_score": hotel.get("recommendation_score"),
    }


def _serialize_restaurant(restaurant: Dict) -> Dict:
    return {
        "id": str(restaurant.get("id", "")),
        "name": restaurant.get("name", ""),
        "city": restaurant.get("city", ""),
        "cuisine": restaurant.get("cuisine", ""),
        "rating": restaurant.get("rating", 0),
        "price_range": restaurant.get("price_range", ""),
        "avg_cost_for_two": restaurant.get("avg_cost_for_two"),
        "opening_hours": restaurant.get("opening_hours"),
        "latitude": restaurant.get("latitude"),
        "longitude": restaurant.get("longitude"),
        "distance_km": restaurant.get("distance_km"),
        "image_url": restaurant.get("image_url"),
        "phone": restaurant.get("phone"),
    }
