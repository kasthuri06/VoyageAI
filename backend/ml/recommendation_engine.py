"""
Voyage AI – Content-Based Recommendation Engine
Uses TF-IDF Vectorization + Cosine Similarity on tourist place features.
Designed to support Collaborative Filtering and Hybrid modes in the future.
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "recommendation_model.pkl"


class ContentBasedRecommender:
    """
    Content-based recommendation engine for tourist places.

    Feature engineering combines:
    - Place category
    - Tags (interests)
    - Description keywords
    - City / State

    Similarity is computed via TF-IDF + Cosine Similarity.
    """

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.places_df: Optional[pd.DataFrame] = None
        self._is_loaded = False

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train(self, df: pd.DataFrame) -> None:
        """Fit the TF-IDF vectorizer on the places dataframe."""
        logger.info(f"Training recommendation model on {len(df)} places...")

        self.places_df = df.copy().reset_index(drop=True)

        # Empty dataset — mark as loaded but no matrix
        if self.places_df.empty:
            self._is_loaded = True
            self.tfidf_matrix = None
            self.vectorizer = None
            logger.warning("Empty dataset — model loaded but cannot make recommendations.")
            return

        # Build feature string for each place
        self.places_df["features"] = self.places_df.apply(self._build_feature_string, axis=1)

        # Filter out empty feature strings before fitting
        non_empty = self.places_df["features"].str.strip().str.len() > 0
        if non_empty.sum() == 0:
            self._is_loaded = True
            self.tfidf_matrix = None
            self.vectorizer = None
            logger.warning("All feature strings are empty — model loaded but cannot make recommendations.")
            return

        # TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            stop_words="english",
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.places_df["features"])

        self._is_loaded = True
        logger.info("Model training complete.")

    def _build_feature_string(self, row: pd.Series) -> str:
        """
        Combine multiple fields into a single feature string for TF-IDF.
        Repeating important fields (tags, category) gives them more weight.
        """
        parts = []

        # Category (repeat for weight)
        if pd.notna(row.get("category")):
            parts.extend([str(row["category"])] * 3)

        # Tags
        tags = row.get("tags", [])
        if isinstance(tags, str):
            try:
                tags = json.loads(tags.replace("'", '"'))
            except Exception:
                tags = []
        if isinstance(tags, list):
            parts.extend(tags * 2)

        # City & State
        if pd.notna(row.get("city")):
            parts.append(str(row["city"]))
        if pd.notna(row.get("state")):
            parts.append(str(row["state"]))

        # Description (lower weight)
        if pd.notna(row.get("description")):
            parts.append(str(row["description"]))

        return " ".join(parts).lower()

    # ------------------------------------------------------------------
    # Saving / Loading
    # ------------------------------------------------------------------
    def save(self, path: Path = MODEL_PATH) -> None:
        """Persist the trained model to disk."""
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        model_data = {
            "vectorizer": self.vectorizer,
            "tfidf_matrix": self.tfidf_matrix,
            "places_df": self.places_df,
        }
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")

    def load(self, path: Path = MODEL_PATH) -> bool:
        """Load model from disk. Returns True if successful."""
        if not path.exists():
            logger.warning(f"Model file not found at {path}. Will train on next request.")
            return False
        try:
            model_data = joblib.load(path)
            self.vectorizer = model_data["vectorizer"]
            self.tfidf_matrix = model_data["tfidf_matrix"]
            self.places_df = model_data["places_df"]
            self._is_loaded = True
            logger.info(f"Model loaded from {path} ({len(self.places_df)} places)")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
    def recommend(
        self,
        interests: List[str],
        city: Optional[str] = None,
        top_n: int = 10,
        exclude_ids: Optional[List[str]] = None,
        weather_is_bad: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Recommend top-N places matching the given interests.

        Args:
            interests:     List of interest strings e.g. ["beach", "nature"]
            city:          Filter by city (optional)
            top_n:         Number of results to return
            exclude_ids:   IDs to exclude (already visited)
            weather_is_bad: If True, prefer indoor places
        """
        if not self._is_loaded:
            logger.error("Model not loaded. Call load() or train() first.")
            return []

        if self.tfidf_matrix is None or self.places_df is None or self.places_df.empty:
            logger.warning("Model loaded but no data available for recommendations.")
            return []

        df = self.places_df.copy()

        # Filter by city if provided
        if city:
            city_lower = city.lower().strip()
            city_mask = df["city"].str.lower().str.contains(city_lower, na=False)
            if city_mask.sum() > 0:
                df = df[city_mask]

        # If weather is bad → prefer indoor places
        if weather_is_bad:
            indoor_mask = df["is_indoor"] == True  # noqa: E712
            if indoor_mask.sum() >= max(2, top_n // 2):
                # Boost indoor but don't exclude outdoor entirely
                indoor_df = df[indoor_mask]
                outdoor_df = df[~indoor_mask]
                df = pd.concat([indoor_df, outdoor_df.sample(
                    min(len(outdoor_df), top_n // 3), random_state=42
                )])

        # Exclude already-visited places
        if exclude_ids:
            df = df[~df["id"].astype(str).isin([str(i) for i in exclude_ids])]

        if df.empty:
            return []

        # Build query vector from interests
        query = " ".join(interests).lower()
        query_vec = self.vectorizer.transform([query])

        # Compute cosine similarity between query and filtered places
        # Re-map indices into the original TF-IDF matrix
        original_indices = df.index.tolist()
        subset_matrix = self.tfidf_matrix[original_indices]
        similarities = cosine_similarity(query_vec, subset_matrix).flatten()

        # Attach similarity scores
        df = df.copy()
        df["similarity_score"] = similarities

        # Sort by similarity, then by rating as tiebreaker
        df = df.sort_values(["similarity_score", "rating"], ascending=[False, False])

        # Return top N
        results = df.head(top_n)
        return results.to_dict(orient="records")

    def get_similar_places(self, place_id: Any, top_n: int = 5) -> List[Dict[str, Any]]:
        """Find places similar to a given place by ID."""
        if not self._is_loaded:
            return []

        df = self.places_df
        mask = df["id"].astype(str) == str(place_id)
        if not mask.any():
            return []

        idx = df[mask].index[0]
        place_vec = self.tfidf_matrix[idx]
        similarities = cosine_similarity(place_vec, self.tfidf_matrix).flatten()
        similarities[idx] = 0  # exclude the place itself

        top_indices = np.argsort(similarities)[::-1][:top_n]
        result = df.iloc[top_indices].copy()
        result["similarity_score"] = similarities[top_indices]
        return result.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Singleton instance loaded at app startup
# ---------------------------------------------------------------------------
recommender = ContentBasedRecommender()


def get_recommender() -> ContentBasedRecommender:
    """Return the loaded recommender, auto-training if needed."""
    global recommender
    if not recommender._is_loaded:
        if not recommender.load():
            # Auto-train from CSV if model file missing
            csv_path = DATASETS_DIR / "tourist_places.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                recommender.train(df)
                recommender.save()
            else:
                logger.error("tourist_places.csv not found — cannot train model")
    return recommender
