# 🌍 Voyage AI – AI-Powered Tourist Route Optimization & Intelligent Itinerary Planning

![Voyage AI Banner](docs/banner.png)

## Overview

Voyage AI is a production-quality, full-stack AI-powered tourism application that helps tourists plan personalized trips by:

- 🗺️ Recommending top tourist attractions based on interests
- 🛣️ Optimizing travel routes using Dijkstra / A* / Google Maps / OpenRouteService
- 🏨 Recommending hotels based on budget, distance, and ratings
- 🍽️ Suggesting nearby restaurants by cuisine and budget
- ☁️ Integrating real-time weather to avoid outdoor plans on rainy days
- 📅 Generating intelligent day-wise itineraries (Morning / Afternoon / Evening / Night)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Tailwind CSS + React Router + Axios |
| Backend | Python + FastAPI + Pydantic + SQLAlchemy |
| ML | Scikit-learn + Pandas + NumPy + Joblib |
| Database | PostgreSQL |
| Auth | JWT Authentication |
| Maps | Google Maps API / OpenRouteService API |
| Weather | OpenWeather API |

---

## Project Structure

```
VoyageAI/
├── frontend/          # React + Vite frontend
├── backend/           # FastAPI backend
│   ├── api/           # Route handlers
│   ├── database/      # Models & migrations
│   ├── ml/            # ML recommendation engine
│   │   ├── datasets/  # CSV datasets
│   │   ├── models/    # Trained model files
│   │   └── notebooks/ # EDA & training notebooks
│   └── tests/         # Unit & integration tests
├── docs/              # API docs & ER diagrams
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Prerequisites
- Node.js >= 18
- Python >= 3.10
- PostgreSQL >= 14
- Docker & Docker Compose (optional)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/VoyageAI.git
cd VoyageAI
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Fill in your API keys
alembic upgrade head      # Run database migrations
python ml/train_model.py  # Train the ML model
uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env      # Fill in your API keys
npm run dev
```

### 4. Docker Setup (Recommended)
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker-compose up --build
```

---

## API Documentation
Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Environment Variables

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql://user:password@localhost:5432/voyageai
SECRET_KEY=your-secret-key
GOOGLE_MAPS_API_KEY=your-google-maps-key
OPENROUTESERVICE_API_KEY=your-ors-key
OPENWEATHER_API_KEY=your-openweather-key
GOOGLE_CLIENT_ID=your-google-client-id
```

### Frontend (`frontend/.env`)
```
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key
```

---

## ML Model

The recommendation engine uses:
- **TF-IDF Vectorization** on attraction descriptions + tags
- **Cosine Similarity** for content-based recommendations
- Trained model saved as `backend/ml/models/recommendation_model.pkl`

To retrain:
```bash
cd backend
python ml/train_model.py
```

---

## License
MIT License — see [LICENSE](LICENSE)
