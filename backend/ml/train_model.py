"""
Voyage AI – Model Training Script
Run: python ml/train_model.py

Performs:
1. Loads tourist_places.csv
2. Feature Engineering
3. Trains TF-IDF + Cosine Similarity recommendation model
4. Evaluates model with sample queries
5. Saves model to ml/models/recommendation_model.pkl
"""
import sys
import logging
from pathlib import Path

import pandas as pd
import numpy as np

# Ensure backend/ is on the path when called as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.recommendation_engine import ContentBasedRecommender, DATASETS_DIR, MODEL_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Load Data
# ---------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    csv_path = DATASETS_DIR / "tourist_places.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} places from CSV")
    return df


# ---------------------------------------------------------------------------
# 2. Feature Engineering
# ---------------------------------------------------------------------------
def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Performing feature engineering...")

    # Fill missing values
    df["description"] = df["description"].fillna("")
    df["category"] = df["category"].fillna("general")
    df["tags"] = df["tags"].fillna("[]")
    df["city"] = df["city"].fillna("Unknown")
    df["state"] = df["state"].fillna("")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)
    df["entry_fee"] = pd.to_numeric(df["entry_fee"], errors="coerce").fillna(0.0)
    df["estimated_duration_hours"] = pd.to_numeric(
        df["estimated_duration_hours"], errors="coerce"
    ).fillna(2.0)
    df["is_indoor"] = df["is_indoor"].map({"true": True, "false": False, True: True, False: False}).fillna(False)

    logger.info(f"Feature engineering complete. Shape: {df.shape}")
    logger.info(f"Categories: {df['category'].value_counts().to_dict()}")
    logger.info(f"Cities: {df['city'].nunique()} unique cities")
    logger.info(f"Avg rating: {df['rating'].mean():.2f}")

    return df


# ---------------------------------------------------------------------------
# 3. Model Evaluation
# ---------------------------------------------------------------------------
def evaluate_model(recommender: ContentBasedRecommender) -> None:
    logger.info("\n--- Model Evaluation ---")

    test_queries = [
        (["beach", "outdoor", "water_sports"], "Goa"),
        (["history", "heritage", "architecture"], "Agra"),
        (["nature", "wildlife", "adventure"], None),
        (["temple", "spiritual", "religious"], None),
        (["museum", "indoor", "family"], "Delhi"),
        (["romantic", "scenic", "couple"], None),
    ]

    for interests, city in test_queries:
        results = recommender.recommend(interests=interests, city=city, top_n=3)
        logger.info(f"\nQuery: interests={interests}, city={city}")
        for i, r in enumerate(results, 1):
            logger.info(f"  {i}. {r['name']} ({r['city']}) — score={r.get('similarity_score', 0):.3f} rating={r['rating']}")

    logger.info("\n✅ Model evaluation complete")


# ---------------------------------------------------------------------------
# 4. Main
# ---------------------------------------------------------------------------
def main():
    logger.info("=" * 50)
    logger.info("Voyage AI – Recommendation Model Training")
    logger.info("=" * 50)

    # Load & preprocess
    df = load_data()
    df = feature_engineering(df)

    # Train
    rec = ContentBasedRecommender()
    rec.train(df)

    # Evaluate
    evaluate_model(rec)

    # Save
    rec.save(MODEL_PATH)
    logger.info(f"\n✅ Model saved to {MODEL_PATH}")
    logger.info("Training pipeline complete.")


if __name__ == "__main__":
    main()
