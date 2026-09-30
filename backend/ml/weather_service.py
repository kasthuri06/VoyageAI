"""
Voyage AI – Weather Service

Fetches real-time and forecast weather from OpenWeather API.
If API key is unavailable, returns a sensible mock response.
"""
import logging
from typing import Dict, Any, Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"


async def get_current_weather(city: str) -> Dict[str, Any]:
    """
    Fetch current weather for a city.

    Returns standardised weather dict:
    {
        city, temperature, feels_like, humidity, description,
        wind_speed, rain_probability, is_bad_weather,
        icon, recommendation
    }
    """
    if not settings.OPENWEATHER_API_KEY:
        return _mock_weather(city)

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                f"{OPENWEATHER_BASE}/weather",
                params={"q": city, "appid": settings.OPENWEATHER_API_KEY, "units": "metric"},
            )
            data = resp.json()

        if resp.status_code != 200:
            logger.warning(f"OpenWeather error for {city}: {data.get('message')}")
            return _mock_weather(city)

        rain_prob = _estimate_rain_probability(data)
        description = data["weather"][0]["description"].capitalize()
        is_bad = rain_prob > 0.5 or _is_extreme_weather(data)

        return {
            "city": city,
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "humidity": data["main"]["humidity"],
            "description": description,
            "wind_speed": data["wind"]["speed"],
            "rain_probability": rain_prob,
            "is_bad_weather": is_bad,
            "icon": data["weather"][0]["icon"],
            "recommendation": _weather_recommendation(is_bad, description),
        }

    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return _mock_weather(city)


async def get_weather_forecast(city: str, days: int = 5) -> Dict[str, Any]:
    """
    Fetch multi-day weather forecast.
    Returns a list of daily forecasts.
    """
    if not settings.OPENWEATHER_API_KEY:
        return _mock_forecast(city, days)

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                f"{OPENWEATHER_BASE}/forecast",
                params={
                    "q": city,
                    "appid": settings.OPENWEATHER_API_KEY,
                    "units": "metric",
                    "cnt": min(days * 8, 40),
                },
            )
            data = resp.json()

        if resp.status_code != 200:
            return _mock_forecast(city, days)

        # Group by day and pick representative noon forecast
        daily = {}
        for item in data["list"]:
            date = item["dt_txt"][:10]
            if date not in daily or "12:00:00" in item["dt_txt"]:
                rain_prob = item.get("pop", 0)
                daily[date] = {
                    "date": date,
                    "temperature": round(item["main"]["temp"], 1),
                    "description": item["weather"][0]["description"].capitalize(),
                    "rain_probability": round(rain_prob, 2),
                    "humidity": item["main"]["humidity"],
                    "icon": item["weather"][0]["icon"],
                    "is_bad_weather": rain_prob > 0.5,
                }

        return {
            "city": city,
            "forecast": list(daily.values())[:days],
        }

    except Exception as e:
        logger.error(f"Weather forecast API error: {e}")
        return _mock_forecast(city, days)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _estimate_rain_probability(data: Dict) -> float:
    """Estimate rain probability from current weather data."""
    weather_id = data["weather"][0]["id"]
    # OWM weather condition codes: 2xx=Thunderstorm, 3xx=Drizzle, 5xx=Rain, 6xx=Snow
    if 200 <= weather_id < 700:
        return 0.8
    if weather_id == 800:
        return 0.0
    if 801 <= weather_id <= 804:
        return 0.1 + (weather_id - 801) * 0.05
    return 0.1


def _is_extreme_weather(data: Dict) -> bool:
    """Return True if conditions are extreme (storm, heavy rain, etc.)."""
    weather_id = data["weather"][0]["id"]
    return weather_id < 300 or (500 <= weather_id < 532) or (600 <= weather_id < 622)


def _weather_recommendation(is_bad: bool, description: str) -> str:
    if is_bad:
        return (
            f"Weather alert: {description}. "
            "We recommend visiting indoor attractions such as museums, galleries, or shopping malls today."
        )
    return f"Great weather! {description}. Perfect for outdoor sightseeing."


def _mock_weather(city: str) -> Dict[str, Any]:
    """Return a mock weather response when API key is unavailable."""
    return {
        "city": city,
        "temperature": 28.0,
        "feels_like": 30.0,
        "humidity": 65,
        "description": "Partly cloudy",
        "wind_speed": 3.5,
        "rain_probability": 0.1,
        "is_bad_weather": False,
        "icon": "02d",
        "recommendation": "Pleasant weather. Great for outdoor sightseeing.",
        "note": "Mock data — configure OPENWEATHER_API_KEY for live data",
    }


def _mock_forecast(city: str, days: int) -> Dict[str, Any]:
    """Return a mock forecast when API key is unavailable."""
    from datetime import date, timedelta

    forecast = []
    for i in range(days):
        d = date.today() + timedelta(days=i)
        forecast.append({
            "date": d.isoformat(),
            "temperature": 27.0 + i,
            "description": "Partly cloudy",
            "rain_probability": 0.1,
            "humidity": 65,
            "icon": "02d",
            "is_bad_weather": False,
        })

    return {
        "city": city,
        "forecast": forecast,
        "note": "Mock data — configure OPENWEATHER_API_KEY for live data",
    }
