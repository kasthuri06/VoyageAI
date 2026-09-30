"""
Voyage AI – Groq AI Service

When a city is searched that doesn't exist in the local CSV dataset,
this module calls the Groq API to generate:
  - Tourist places
  - Hotels
  - Restaurants

Model priority (tried in order until one succeeds):
  1. GROQ_MODEL env var (user-configurable)
  2. llama-3.1-8b-instant
  3. openai/gpt-oss-20b
  4. qwen/qwen3.8-27b

Results are cached in-memory so the same city isn't fetched twice per session.
"""
import json
import logging
import re
from typing import List, Dict, Any, Optional

from config import settings

logger = logging.getLogger(__name__)

# In-memory cache: city_lower → {"places": [...], "hotels": [...], "restaurants": [...]}
_groq_cache: Dict[str, Dict] = {}

# Ordered list of models to try — first one that works wins.
# These are the text-generation models available on the free Groq developer tier.
_MODEL_FALLBACK_CHAIN = [
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
]


def _get_groq_client():
    """Return a Groq client if API key is configured."""
    if not settings.GROQ_API_KEY:
        return None
    try:
        from groq import Groq
        return Groq(api_key=settings.GROQ_API_KEY)
    except ImportError:
        logger.error("groq package not installed. Run: pip install groq")
        return None


def _call_groq(client, prompt: str, max_tokens: int = 3000) -> Optional[str]:
    """
    Call Groq with automatic model fallback.

    Tries models in this order:
      1. settings.GROQ_MODEL (if set explicitly in .env)
      2. _MODEL_FALLBACK_CHAIN entries one by one

    Returns the raw text content, or None if all models fail.
    """
    import time

    # Build the ordered list to try
    models_to_try: List[str] = []
    if settings.GROQ_MODEL:
        models_to_try.append(settings.GROQ_MODEL)
    for m in _MODEL_FALLBACK_CHAIN:
        if m not in models_to_try:
            models_to_try.append(m)

    for model in models_to_try:
        for attempt in range(2):  # 1 retry on rate limit
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=max_tokens,
                )
                logger.info(f"[Groq] Using model: {model}")
                return response.choices[0].message.content
            except Exception as e:
                err_str = str(e)
                if "model_not_found" in err_str or "404" in err_str or "does not exist" in err_str:
                    logger.warning(f"[Groq] Model '{model}' unavailable, trying next... ({err_str[:80]})")
                    break  # try next model
                if ("rate_limit" in err_str or "429" in err_str) and attempt == 0:
                    logger.warning(f"[Groq] Rate limit hit, waiting 10s before retry...")
                    import time as _time
                    _time.sleep(10)
                    continue  # retry same model
                raise  # unexpected error

    logger.error("[Groq] All models in fallback chain failed.")
    return None


def _extract_json(text: str) -> Any:
    """
    Extract a JSON array from LLM response.
    Handles markdown code fences and truncated responses by recovering
    all complete objects even if the array was cut off mid-stream.
    """
    # Strip markdown fences
    text = re.sub(r"```(?:json)?", "", text).strip()
    text = text.replace("```", "").strip()

    # Find the start of the array
    start = text.find("[")
    if start == -1:
        # Try single object
        start = text.find("{")
        if start == -1:
            return None
        end = text.rfind("}")
        if end == -1:
            return None
        return json.loads(text[start:end + 1])

    # Try the full array first
    end = text.rfind("]")
    if end != -1:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass  # fall through to partial recovery

    # Partial recovery: find all complete {...} objects inside the array
    objects = []
    depth = 0
    obj_start = None
    i = start + 1  # skip the opening [
    in_string = False
    escape_next = False

    while i < len(text):
        ch = text[i]

        if escape_next:
            escape_next = False
        elif ch == '\\' and in_string:
            escape_next = True
        elif ch == '"' and not escape_next:
            in_string = not in_string
        elif not in_string:
            if ch == '{':
                if depth == 0:
                    obj_start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and obj_start is not None:
                    try:
                        obj = json.loads(text[obj_start:i + 1])
                        objects.append(obj)
                    except json.JSONDecodeError:
                        pass
                    obj_start = None
        i += 1

    if objects:
        logger.warning(f"[Groq] Partial JSON recovery: got {len(objects)} complete objects")
        return objects

    return None


async def generate_places_for_city(city: str, state: str = "", country: str = "India") -> List[Dict[str, Any]]:
    """
    Generate tourist place data for a given city using Groq LLM.
    Returns list of place dicts compatible with TouristPlace schema.
    """
    cache_key = f"places:{city.lower().strip()}"
    if cache_key in _groq_cache:
        logger.info(f"[Groq cache hit] places for {city}")
        return _groq_cache[cache_key]

    client = _get_groq_client()
    if not client:
        logger.warning("Groq API key not set — cannot generate places")
        return []

    prompt = f"""Return a JSON array of 8 real tourist attractions in {city}, {state or country}.
Each item: {{"name":"...","description":"1 sentence.","city":"{city}","state":"{state or city}","country":"{country}","latitude":0.0,"longitude":0.0,"category":"monument","tags":["tag1","tag2"],"rating":4.2,"entry_fee":0,"opening_hours":"09:00-18:00","is_indoor":false,"estimated_duration_hours":2.0,"best_time_to_visit":"Oct-Mar","image_url":""}}
Use real GPS coordinates for {city}. Return ONLY valid JSON array, no markdown, no text."""

    try:
        raw = _call_groq(client, prompt, max_tokens=4000)
        if raw is None:
            return []
        data = _extract_json(raw)
        if not isinstance(data, list):
            logger.error(f"Groq returned non-list for places: {raw[:200]}")
            return []

        # Validate and sanitise each place
        places = []
        for item in data:
            if not isinstance(item, dict):
                continue
            place = {
                "id": f"groq_{city.lower()}_{len(places)}",
                "name": str(item.get("name", f"Place in {city}")),
                "description": str(item.get("description", "")),
                "city": city,
                "state": state or city,
                "country": country,
                "latitude": float(item.get("latitude", 0)),
                "longitude": float(item.get("longitude", 0)),
                "category": str(item.get("category", "monument")),
                "tags": item.get("tags", []),
                "rating": float(item.get("rating", 4.0)),
                "entry_fee": float(item.get("entry_fee", 0)),
                "opening_hours": str(item.get("opening_hours", "09:00-18:00")),
                "is_indoor": bool(item.get("is_indoor", False)),
                "estimated_duration_hours": float(item.get("estimated_duration_hours", 2.0)),
                "best_time_to_visit": str(item.get("best_time_to_visit", "October to March")),
                "image_url": str(item.get("image_url", "")),
                "_source": "groq",
            }
            # Skip if coordinates are missing/zero
            if place["latitude"] == 0 and place["longitude"] == 0:
                continue
            places.append(place)

        _groq_cache[cache_key] = places
        logger.info(f"[Groq] Generated {len(places)} places for {city}")
        return places

    except Exception as e:
        logger.error(f"Groq places error for {city}: {e}")
        return []


async def generate_hotels_for_city(city: str, state: str = "", country: str = "India") -> List[Dict[str, Any]]:
    """Generate hotel data for a given city using Groq LLM."""
    cache_key = f"hotels:{city.lower().strip()}"
    if cache_key in _groq_cache:
        return _groq_cache[cache_key]

    client = _get_groq_client()
    if not client:
        return []

    prompt = f"""Return a JSON array of 6 real hotels in {city}, {state or country} across price ranges.
Each item: {{"name":"...","description":"1 sentence.","city":"{city}","address":"area, {city}","latitude":0.0,"longitude":0.0,"star_rating":3,"user_rating":4.0,"price_per_night":3000,"amenities":["wifi","parking"],"phone":"+91-xxx","website":"","image_url":""}}
Use real GPS coordinates near {city} center. Return ONLY valid JSON array, no markdown, no text."""

    try:
        raw = _call_groq(client, prompt, max_tokens=3000)
        if raw is None:
            return []
        data = _extract_json(raw)
        if not isinstance(data, list):
            return []

        hotels = []
        for item in data:
            if not isinstance(item, dict):
                continue
            hotel = {
                "id": f"groq_hotel_{city.lower()}_{len(hotels)}",
                "name": str(item.get("name", f"Hotel in {city}")),
                "description": str(item.get("description", "")),
                "city": city,
                "address": str(item.get("address", city)),
                "latitude": float(item.get("latitude", 0)),
                "longitude": float(item.get("longitude", 0)),
                "star_rating": int(item.get("star_rating", 3)),
                "user_rating": float(item.get("user_rating", 4.0)),
                "price_per_night": float(item.get("price_per_night", 3000)),
                "amenities": item.get("amenities", ["wifi"]),
                "phone": str(item.get("phone", "")),
                "website": "",
                "image_url": "",
                "_source": "groq",
            }
            if hotel["latitude"] == 0 and hotel["longitude"] == 0:
                continue
            hotels.append(hotel)

        _groq_cache[cache_key] = hotels
        logger.info(f"[Groq] Generated {len(hotels)} hotels for {city}")
        return hotels

    except Exception as e:
        logger.error(f"Groq hotels error for {city}: {e}")
        return []


async def generate_restaurants_for_city(city: str, state: str = "", country: str = "India") -> List[Dict[str, Any]]:
    """Generate restaurant data for a given city using Groq LLM."""
    cache_key = f"restaurants:{city.lower().strip()}"
    if cache_key in _groq_cache:
        return _groq_cache[cache_key]

    client = _get_groq_client()
    if not client:
        return []

    prompt = f"""Return a JSON array of 6 real restaurants in {city}, {state or country} with varied cuisines.
Each item: {{"name":"...","description":"1 sentence.","city":"{city}","address":"area, {city}","latitude":0.0,"longitude":0.0,"cuisine":"North Indian","rating":4.1,"price_range":"₹₹","avg_cost_for_two":500,"opening_hours":"09:00-22:00","phone":"+91-xxx","image_url":""}}
Use real GPS coordinates near {city} center. Return ONLY valid JSON array, no markdown, no text."""

    try:
        raw = _call_groq(client, prompt, max_tokens=3000)
        if raw is None:
            return []
        data = _extract_json(raw)
        if not isinstance(data, list):
            return []

        restaurants = []
        for item in data:
            if not isinstance(item, dict):
                continue
            restaurant = {
                "id": f"groq_rest_{city.lower()}_{len(restaurants)}",
                "name": str(item.get("name", f"Restaurant in {city}")),
                "description": str(item.get("description", "")),
                "city": city,
                "address": str(item.get("address", city)),
                "latitude": float(item.get("latitude", 0)),
                "longitude": float(item.get("longitude", 0)),
                "cuisine": str(item.get("cuisine", "Indian")),
                "rating": float(item.get("rating", 4.0)),
                "price_range": str(item.get("price_range", "₹₹")),
                "avg_cost_for_two": float(item.get("avg_cost_for_two", 500)),
                "opening_hours": str(item.get("opening_hours", "09:00-22:00")),
                "phone": str(item.get("phone", "")),
                "image_url": "",
                "_source": "groq",
            }
            if restaurant["latitude"] == 0 and restaurant["longitude"] == 0:
                continue
            restaurants.append(restaurant)

        _groq_cache[cache_key] = restaurants
        logger.info(f"[Groq] Generated {len(restaurants)} restaurants for {city}")
        return restaurants

    except Exception as e:
        logger.error(f"Groq restaurants error for {city}: {e}")
        return []


async def get_city_data(city: str) -> Dict[str, List]:
    """
    Fetch all data for a city — places, hotels, restaurants — in one call.
    """
    # Try to infer state from common Indian cities
    state = _infer_state(city)
    places, hotels, restaurants = await _gather(city, state)
    return {"places": places, "hotels": hotels, "restaurants": restaurants}


async def _gather(city: str, state: str):
    """Run all three Groq calls sequentially to avoid rate limit (8K TPM)."""
    import asyncio
    places      = await generate_places_for_city(city, state)
    # Small delay between calls to respect rate limits
    await asyncio.sleep(1.5)
    hotels      = await generate_hotels_for_city(city, state)
    await asyncio.sleep(1.5)
    restaurants = await generate_restaurants_for_city(city, state)
    return places, hotels, restaurants


def _infer_state(city: str) -> str:
    """Map common Indian cities to their state."""
    city_state = {
        "chennai": "Tamil Nadu",
        "coimbatore": "Tamil Nadu",
        "madurai": "Tamil Nadu",
        "trichy": "Tamil Nadu",
        "tiruchirappalli": "Tamil Nadu",
        "salem": "Tamil Nadu",
        "vellore": "Tamil Nadu",
        "tirunelveli": "Tamil Nadu",
        "pondicherry": "Puducherry",
        "puducherry": "Puducherry",
        "hyderabad": "Telangana",
        "warangal": "Telangana",
        "bangalore": "Karnataka",
        "bengaluru": "Karnataka",
        "mysore": "Karnataka",
        "mysuru": "Karnataka",
        "hubli": "Karnataka",
        "mangalore": "Karnataka",
        "kochi": "Kerala",
        "thiruvananthapuram": "Kerala",
        "kozhikode": "Kerala",
        "thrissur": "Kerala",
        "mumbai": "Maharashtra",
        "pune": "Maharashtra",
        "nagpur": "Maharashtra",
        "nashik": "Maharashtra",
        "aurangabad": "Maharashtra",
        "delhi": "Delhi",
        "new delhi": "Delhi",
        "kolkata": "West Bengal",
        "darjeeling": "West Bengal",
        "ahmedabad": "Gujarat",
        "surat": "Gujarat",
        "vadodara": "Gujarat",
        "jaipur": "Rajasthan",
        "jodhpur": "Rajasthan",
        "udaipur": "Rajasthan",
        "jaisalmer": "Rajasthan",
        "lucknow": "Uttar Pradesh",
        "agra": "Uttar Pradesh",
        "varanasi": "Uttar Pradesh",
        "kanpur": "Uttar Pradesh",
        "allahabad": "Uttar Pradesh",
        "prayagraj": "Uttar Pradesh",
        "bhopal": "Madhya Pradesh",
        "indore": "Madhya Pradesh",
        "gwalior": "Madhya Pradesh",
        "khajuraho": "Madhya Pradesh",
        "chandigarh": "Punjab",
        "amritsar": "Punjab",
        "ludhiana": "Punjab",
        "dehradun": "Uttarakhand",
        "rishikesh": "Uttarakhand",
        "haridwar": "Uttarakhand",
        "nainital": "Uttarakhand",
        "mussoorie": "Uttarakhand",
        "shimla": "Himachal Pradesh",
        "manali": "Himachal Pradesh",
        "dharamshala": "Himachal Pradesh",
        "leh": "Ladakh",
        "srinagar": "Jammu & Kashmir",
        "jammu": "Jammu & Kashmir",
        "bhubaneswar": "Odisha",
        "puri": "Odisha",
        "patna": "Bihar",
        "bodh gaya": "Bihar",
        "ranchi": "Jharkhand",
        "guwahati": "Assam",
        "shillong": "Meghalaya",
        "gangtok": "Sikkim",
        "aizawl": "Mizoram",
        "imphal": "Manipur",
        "agartala": "Tripura",
        "port blair": "Andaman & Nicobar",
        "panaji": "Goa",
        "panjim": "Goa",
        "goa": "Goa",
        "raipur": "Chhattisgarh",
        "visakhapatnam": "Andhra Pradesh",
        "vijayawada": "Andhra Pradesh",
        "tirupati": "Andhra Pradesh",
    }
    return city_state.get(city.lower().strip(), "")


def clear_cache(city: str = None):
    """Clear Groq cache — all cities or a specific city."""
    global _groq_cache
    if city:
        keys = [k for k in _groq_cache if city.lower() in k]
        for k in keys:
            del _groq_cache[k]
    else:
        _groq_cache.clear()
