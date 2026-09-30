# Voyage AI – Installation Guide

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | ≥ 3.10 | https://python.org |
| Node.js | ≥ 18 | https://nodejs.org |
| PostgreSQL | ≥ 14 | https://postgresql.org |
| Git | any | https://git-scm.com |
| Docker | ≥ 24 (optional) | https://docker.com |

---

## Step 1: Clone the Project

```bash
git clone https://github.com/yourorg/VoyageAI.git
cd VoyageAI
```

---

## Step 2: Database Setup

```bash
# Connect as postgres superuser
psql -U postgres

# Run these SQL commands:
CREATE DATABASE voyageai;
CREATE USER voyageai WITH ENCRYPTED PASSWORD 'voyageai123';
GRANT ALL PRIVILEGES ON DATABASE voyageai TO voyageai;
\q
```

---

## Step 3: Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and set your API keys

# Run database migrations
alembic upgrade head

# Train the ML recommendation model
python ml/train_model.py
# Output: backend/ml/models/recommendation_model.pkl

# Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for the Swagger UI.

---

## Step 4: Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

Visit http://localhost:5173

---

## Step 5: Verify Installation

1. Open http://localhost:5173 — Landing page should load
2. Register a new account at `/register`
3. Go to `/plan`, fill in a trip (e.g. Mumbai → Goa, 3 days, interests: beach, food)
4. Click "Generate AI Itinerary" — should return a day-wise plan
5. Save the trip and view it at `/saved`

---

## Step 6: Create Admin User (Optional)

```bash
cd backend
python -c "
from database.session import SessionLocal
from database.models import User, UserRole
from core.security import hash_password
import uuid

db = SessionLocal()
admin = User(
    email='admin@voyage.ai',
    username='admin',
    hashed_password=hash_password('Admin@123'),
    role=UserRole.admin,
    is_active=True,
    is_verified=True,
)
db.add(admin)
db.commit()
print('Admin user created: admin@voyage.ai / Admin@123')
"
```

Then visit http://localhost:5173/admin

---

## Optional: Seed Database from CSVs

After creating the admin user, log in and visit `/admin` → Upload Data tab to upload:
- `backend/ml/datasets/tourist_places.csv`
- `backend/ml/datasets/hotels.csv`
- `backend/ml/datasets/restaurants.csv`

---

## Troubleshooting

**`ModuleNotFoundError`** — Ensure virtual env is activated: `source venv/bin/activate`

**`Connection refused` on DB** — Check PostgreSQL is running: `sudo service postgresql start`

**ML model not found** — Run: `cd backend && python ml/train_model.py`

**CORS errors** — Ensure `CORS_ORIGINS` in `.env` includes your frontend URL
