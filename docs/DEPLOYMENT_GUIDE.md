# Voyage AI – Deployment Guide

## 1. Docker Compose (Recommended)

```bash
# Clone repo
git clone https://github.com/yourorg/VoyageAI.git
cd VoyageAI

# Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit both .env files with your API keys

# Build and start all services
docker-compose up --build -d

# Services running:
# PostgreSQL  → localhost:5432
# Backend API → localhost:8000  (Swagger: /docs)
# Frontend    → localhost:5173
```

---

## 2. Manual Setup (Development)

### PostgreSQL
```bash
psql -U postgres -c "CREATE DATABASE voyageai;"
psql -U postgres -c "CREATE USER voyageai WITH PASSWORD 'voyageai123';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE voyageai TO voyageai;"
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Edit with your keys

# Run migrations
alembic upgrade head

# Train ML model
python ml/train_model.py

# Start API server
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env             # Set VITE_API_BASE_URL
npm run dev                      # Dev server at http://localhost:5173
```

---

## 3. Production Deployment

### Backend (Gunicorn + Nginx)
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /var/log/voyageai/access.log
```

### Frontend (Static Build)
```bash
cd frontend
npm run build                    # Outputs to dist/
# Serve dist/ with Nginx or upload to CDN (Vercel, Netlify, S3+CloudFront)
```

### Nginx Proxy Config (Backend)
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120;
    }
}
```

---

## 4. Environment Variables Reference

### Backend
| Variable | Required | Description |
|---|---|---|
| DATABASE_URL | ✅ | PostgreSQL connection string |
| SECRET_KEY | ✅ | JWT signing secret (32+ chars) |
| OPENWEATHER_API_KEY | Recommended | Live weather data |
| GOOGLE_MAPS_API_KEY | Optional | Google routing |
| OPENROUTESERVICE_API_KEY | Optional | ORS routing |
| GOOGLE_CLIENT_ID | Optional | Google OAuth |
| ROUTING_MODE | - | algorithm/google/ors (default: algorithm) |

### Frontend
| Variable | Required | Description |
|---|---|---|
| VITE_API_BASE_URL | ✅ | Backend URL |
| VITE_GOOGLE_MAPS_API_KEY | Optional | Google Maps embed |

---

## 5. Monitoring & Logs

```bash
# View backend logs
docker-compose logs -f backend

# PostgreSQL stats
docker exec -it voyageai_db psql -U voyageai -d voyageai -c "\dt"
```

---

## 6. Scaling

- Use a managed PostgreSQL (AWS RDS / Supabase / Neon)
- Deploy backend to AWS ECS / Railway / Fly.io
- Deploy frontend to Vercel / Netlify
- Use Redis for JWT blacklisting (optional)
- Add Celery + Redis for async itinerary generation at scale
