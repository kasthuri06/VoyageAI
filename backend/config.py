"""
Application configuration — loaded from environment variables / .env file.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database — SQLite by default (zero config), switch to PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./voyageai.db"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Maps
    GOOGLE_MAPS_API_KEY: str = ""
    OPENROUTESERVICE_API_KEY: str = ""

    # Weather
    OPENWEATHER_API_KEY: str = ""

    # Groq — for AI-generated place data when city not in CSV
    GROQ_API_KEY: str = ""
    # Override the Groq model (leave empty to use auto-fallback chain)
    GROQ_MODEL: str = ""

    # Routing mode: "algorithm" | "google" | "ors"
    ROUTING_MODE: str = "algorithm"

    # App
    APP_ENV: str = "development"

    # CORS — accept JSON array string OR comma-separated OR plain list
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            # JSON array format: ["url1","url2"]
            if v.startswith("["):
                import json
                return json.loads(v)
            # Comma-separated: url1,url2
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
