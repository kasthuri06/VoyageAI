"""
Unit tests for the ML recommendation engine.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.recommendation_engine import ContentBasedRecommender


@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {
            "id": 1, "name": "Baga Beach", "description": "Popular beach with water sports",
            "city": "Goa", "state": "Goa", "country": "India",
            "latitude": 15.55, "longitude": 73.75, "category": "beach",
            "tags": ["beach", "adventure", "water_sports"], "rating": 4.3,
            "entry_fee": 0, "is_indoor": False, "estimated_duration_hours": 4.0,
        },
        {
            "id": 2, "name": "Taj Mahal", "description": "Iconic monument and heritage site",
            "city": "Agra", "state": "UP", "country": "India",
            "latitude": 27.17, "longitude": 78.04, "category": "monument",
            "tags": ["history", "heritage", "romantic"], "rating": 4.9,
            "entry_fee": 1100, "is_indoor": False, "estimated_duration_hours": 3.0,
        },
        {
            "id": 3, "name": "National Museum Delhi", "description": "Premier museum in Delhi",
            "city": "Delhi", "state": "Delhi", "country": "India",
            "latitude": 28.61, "longitude": 77.22, "category": "museum",
            "tags": ["museum", "indoor", "history", "family"], "rating": 4.2,
            "entry_fee": 300, "is_indoor": True, "estimated_duration_hours": 3.0,
        },
    ])


@pytest.fixture
def trained_recommender(sample_df):
    rec = ContentBasedRecommender()
    rec.train(sample_df)
    return rec


def test_train_loads_data(trained_recommender):
    assert trained_recommender._is_loaded
    assert len(trained_recommender.places_df) == 3


def test_recommend_beach(trained_recommender):
    results = trained_recommender.recommend(interests=["beach", "water_sports"], top_n=3)
    assert len(results) > 0
    # Top result should be Baga Beach
    assert results[0]["name"] == "Baga Beach"


def test_recommend_with_city_filter(trained_recommender):
    results = trained_recommender.recommend(interests=["museum"], city="Delhi", top_n=3)
    assert all("Delhi" in r["city"] for r in results)


def test_recommend_bad_weather_prefers_indoor(trained_recommender):
    results = trained_recommender.recommend(
        interests=["family", "history"],
        weather_is_bad=True,
        top_n=3,
    )
    # National Museum is indoor — should appear in results
    names = [r["name"] for r in results]
    assert "National Museum Delhi" in names


def test_similar_places(trained_recommender):
    similar = trained_recommender.get_similar_places(place_id=1, top_n=2)
    assert len(similar) <= 2
    # Should not contain the query place itself
    assert all(str(r["id"]) != "1" for r in similar)


def test_recommend_empty_dataset():
    rec = ContentBasedRecommender()
    rec.train(pd.DataFrame(columns=["id", "name", "city", "category", "tags", "description",
                                     "latitude", "longitude", "rating", "is_indoor",
                                     "entry_fee", "estimated_duration_hours"]))
    results = rec.recommend(interests=["beach"])
    assert results == []
