"""
Voyage AI – FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from config import settings
from database.session import engine, Base
from api.routes import auth, users, recommend, routes, weather, hotels, restaurants, trips, history, reviews, admin

# ---------------------------------------------------------------------------
# Initialise FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Voyage AI",
    description="AI-Powered Tourist Route Optimization & Intelligent Itinerary Planning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins in development, restrict in production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # open for local dev; tighten in prod
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup / Shutdown
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    logger.info("🚀 Voyage AI backend starting up...")
    # For SQLite (local dev): create tables directly via SQLAlchemy.
    # For PostgreSQL (production): use `alembic upgrade head` instead.
    from config import settings
    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        logger.info("✅ SQLite database tables created")
    else:
        logger.info("✅ Using PostgreSQL — run 'alembic upgrade head' to migrate")

    # Auto-train ML model if not already trained
    try:
        from ml.recommendation_engine import get_recommender
        get_recommender()
        logger.info("✅ ML recommendation model ready")
    except Exception as e:
        logger.warning(f"⚠️  ML model not ready: {e}")


@app.on_event("shutdown")
async def shutdown():
    logger.info("🔴 Voyage AI backend shutting down...")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": "Voyage AI", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router,        prefix="/auth",        tags=["Authentication"])
app.include_router(users.router,       prefix="/user",        tags=["Users"])
app.include_router(recommend.router,   prefix="/recommend",   tags=["Recommendations"])
app.include_router(routes.router,      prefix="/routes",      tags=["Route Optimization"])
app.include_router(weather.router,     prefix="/weather",     tags=["Weather"])
app.include_router(hotels.router,      prefix="/hotels",      tags=["Hotels"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
app.include_router(trips.router,       prefix="/trips",       tags=["Trips"])
app.include_router(history.router,     prefix="/history",     tags=["User History"])
app.include_router(reviews.router,     prefix="/reviews",     tags=["Reviews"])
app.include_router(admin.router,       prefix="/admin",       tags=["Admin"])
