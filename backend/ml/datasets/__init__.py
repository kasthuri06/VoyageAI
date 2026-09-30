"""
Dataset loader helpers — reads CSVs from the datasets/ directory.
Used as fallback when the database is empty.
"""
import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)
DATASETS_DIR = Path(__file__).parent


def _parse_tags(val):
    """Parse tag field that may be a JSON string or Python list literal."""
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val.replace("'", '"'))
        except Exception:
            return []
    return []


def load_places_df() -> pd.DataFrame:
    path = DATASETS_DIR / "tourist_places.csv"
    if not path.exists():
        logger.error(f"Dataset not found: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["tags"] = df["tags"].apply(_parse_tags)
    df["is_indoor"] = df["is_indoor"].map(
        {"true": True, "false": False, True: True, False: False}
    ).fillna(False)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)
    df["entry_fee"] = pd.to_numeric(df["entry_fee"], errors="coerce").fillna(0.0)
    df["estimated_duration_hours"] = pd.to_numeric(
        df["estimated_duration_hours"], errors="coerce"
    ).fillna(2.0)
    return df


def load_hotels_df() -> pd.DataFrame:
    path = DATASETS_DIR / "hotels.csv"
    if not path.exists():
        logger.error(f"Dataset not found: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["amenities"] = df["amenities"].apply(_parse_tags)
    df["price_per_night"] = pd.to_numeric(df["price_per_night"], errors="coerce").fillna(0.0)
    df["user_rating"] = pd.to_numeric(df["user_rating"], errors="coerce").fillna(0.0)
    df["star_rating"] = pd.to_numeric(df["star_rating"], errors="coerce").fillna(3)
    return df


def load_restaurants_df() -> pd.DataFrame:
    path = DATASETS_DIR / "restaurants.csv"
    if not path.exists():
        logger.error(f"Dataset not found: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)
    df["avg_cost_for_two"] = pd.to_numeric(df["avg_cost_for_two"], errors="coerce").fillna(0.0)
    return df
