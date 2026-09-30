"""
Weather routes: /weather/current, /weather/forecast
"""
from fastapi import APIRouter, Query
from ml.weather_service import get_current_weather, get_weather_forecast

router = APIRouter()


@router.get("/current")
async def current_weather(city: str = Query(..., example="Mumbai")):
    """Fetch current weather for a city."""
    return await get_current_weather(city)


@router.get("/forecast")
async def forecast(
    city: str = Query(..., example="Goa"),
    days: int = Query(5, ge=1, le=14),
):
    """Fetch multi-day weather forecast for a city."""
    return await get_weather_forecast(city, days=days)
