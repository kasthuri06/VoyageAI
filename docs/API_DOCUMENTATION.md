# Voyage AI – API Documentation

Base URL: `http://localhost:8000`  
Interactive Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 🔐 Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT |
| POST | `/auth/google` | Google OAuth login |

**Register Request:**
```json
{
  "email": "user@example.com",
  "username": "explorer",
  "password": "SecurePass123",
  "full_name": "Jane Doe"
}
```

**Login Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user_id": "uuid",
  "username": "explorer",
  "role": "user"
}
```

---

### 👤 Users

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/user/profile` | ✅ | Get current user profile |
| PUT | `/user/profile` | ✅ | Update profile |
| GET | `/user/preferences` | ✅ | Get travel preferences |
| PUT | `/user/preferences` | ✅ | Update travel preferences |
| GET | `/user/saved-trips` | ✅ | Get saved trips |
| GET | `/user/favorite-places` | ✅ | Get favourite places |

---

### ✨ Recommendations (ML Engine)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/recommend/itinerary` | ✅ | **Main AI pipeline** — full itinerary |
| GET | `/recommend/places` | - | List places (city, category filter) |
| GET | `/recommend/similar/{place_id}` | - | Find similar places |

**Itinerary Request:**
```json
{
  "start_location": "Mumbai",
  "end_location": "Goa",
  "travel_days": 3,
  "budget": 15000,
  "transport_mode": "car",
  "interests": ["beach", "food", "nature"],
  "group_size": 2,
  "preferred_hotel_rating": 3,
  "travel_style": "couple",
  "preferred_travel_time": "morning"
}
```

---

### 🛣️ Route Optimization

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/routes/optimize` | - | Optimise visitation order |
| POST | `/routes/directions` | - | Turn-by-turn directions |

**Optimize Request:**
```json
{
  "places": [
    {"name": "Baga Beach", "latitude": 15.55, "longitude": 73.75},
    {"name": "Dudhsagar Falls", "latitude": 15.31, "longitude": 74.31}
  ],
  "transport_mode": "car"
}
```

---

### ☁️ Weather

| Method | Path | Description |
|--------|------|-------------|
| GET | `/weather/current?city=Goa` | Current weather |
| GET | `/weather/forecast?city=Goa&days=5` | 5-day forecast |

---

### 🏨 Hotels

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/hotels/` | - | List hotels |
| POST | `/hotels/recommend` | - | Get recommendations |

**Recommend Request:**
```json
{
  "city": "Goa",
  "budget_per_night": 5000,
  "latitude": 15.49,
  "longitude": 73.83,
  "min_star_rating": 3,
  "amenities": ["wifi", "pool"],
  "top_n": 5
}
```

---

### 🍽️ Restaurants

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/restaurants/` | - | List restaurants |
| POST | `/restaurants/recommend` | - | Get nearby recommendations |

---

### 🗺️ Trips

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/trips/` | ✅ | Save a new trip |
| GET | `/trips/` | ✅ | List user trips |
| GET | `/trips/{id}` | ✅ | Get trip details |
| PUT | `/trips/{id}/save` | ✅ | Toggle saved |
| PUT | `/trips/{id}/status` | ✅ | Update status |
| DELETE | `/trips/{id}` | ✅ | Delete trip |

---

### 📋 History

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/history/` | ✅ | Get activity history |
| POST | `/history/log` | ✅ | Log an action |

---

### ⭐ Reviews

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/reviews/` | ✅ | Submit a review |
| GET | `/reviews/place/{id}` | - | Get place reviews |

---

### 🔧 Admin

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/analytics` | Admin | System analytics |
| GET | `/admin/users` | Admin | List all users |
| PUT | `/admin/users/{id}/deactivate` | Admin | Deactivate user |
| PUT | `/admin/users/{id}/make-admin` | Admin | Grant admin |
| POST | `/admin/upload/places` | Admin | Upload places CSV |
| POST | `/admin/upload/hotels` | Admin | Upload hotels CSV |
| POST | `/admin/upload/restaurants` | Admin | Upload restaurants CSV |

---

## Error Responses

```json
{
  "detail": "Invalid or expired token"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation error |
| 401 | Unauthorized — invalid/missing token |
| 403 | Forbidden — insufficient permissions |
| 404 | Resource not found |
| 422 | Unprocessable entity |
| 500 | Internal server error |
