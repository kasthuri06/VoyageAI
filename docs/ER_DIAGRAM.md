# Voyage AI – Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         VOYAGE AI DATABASE                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────────────┐
│    USERS     │         │   USER_PREFERENCES    │
├──────────────┤         ├──────────────────────┤
│ id (PK)      │─────────│ id (PK)              │
│ email        │  1   1  │ user_id (FK→users)   │
│ username     │         │ interests (JSON)      │
│ hashed_pwd   │         │ preferred_transport   │
│ full_name    │         │ preferred_hotel_rating│
│ profile_pic  │         │ max_budget_per_day    │
│ phone        │         │ travel_style          │
│ role         │         │ preferred_cuisine     │
│ is_active    │         │ preferred_travel_time │
│ is_verified  │         └──────────────────────┘
│ google_id    │
│ created_at   │
└──────┬───────┘
       │ 1
       │
       ├──────────────────────────────────────────┐
       │ 1..N                                      │ 1..N
       │                                           │
       ▼                                           ▼
┌──────────────┐                        ┌──────────────────┐
│    TRIPS     │                        │     REVIEWS      │
├──────────────┤                        ├──────────────────┤
│ id (PK)      │                        │ id (PK)          │
│ user_id (FK) │                        │ user_id (FK)     │
│ title        │                        │ place_id (FK,opt)│
│ start_loc    │                        │ hotel_id (FK,opt)│
│ end_loc      │                        │ restaurant_id    │
│ travel_days  │                        │ rating           │
│ budget       │                        │ comment          │
│ transport    │                        │ created_at       │
│ group_size   │                        └───────┬──────────┘
│ status       │                                │ N
│ itinerary    │                                │
│ total_cost   │                        ┌───────▼──────────┐
│ is_saved     │                        │  TOURIST_PLACES  │
│ created_at   │                        ├──────────────────┤
└──────┬───────┘                        │ id (PK)          │
       │ 1..N                           │ name             │
       │                                │ description      │
       ▼                                │ city             │
┌──────────────────┐                    │ state            │
│   USER_HISTORY   │                    │ country          │
├──────────────────┤                    │ latitude         │
│ id (PK)          │                    │ longitude        │
│ user_id (FK)     │                    │ category         │
│ place_id (FK,opt)│                    │ tags (JSON)      │
│ trip_id (FK,opt) │                    │ rating           │
│ action           │                    │ entry_fee        │
│ metadata (JSON)  │                    │ opening_hours    │
│ created_at       │                    │ is_indoor        │
└──────────────────┘                    │ est_duration     │
                                        │ image_url        │
┌──────────────────┐                    └──────────────────┘
│      HOTELS      │
├──────────────────┤
│ id (PK)          │
│ name             │
│ city             │
│ address          │
│ latitude         │
│ longitude        │
│ star_rating      │
│ user_rating      │
│ price_per_night  │
│ amenities (JSON) │
│ image_url        │
│ phone / website  │
└──────────────────┘

┌──────────────────┐
│   RESTAURANTS    │
├──────────────────┤
│ id (PK)          │
│ name             │
│ city             │
│ cuisine          │
│ rating           │
│ price_range      │
│ avg_cost_for_two │
│ latitude         │
│ longitude        │
│ opening_hours    │
└──────────────────┘
```

## Relationships Summary

| Relationship | Cardinality |
|---|---|
| User → UserPreference | 1:1 |
| User → Trips | 1:N |
| User → Reviews | 1:N |
| User → UserHistory | 1:N |
| TouristPlace → Reviews | 1:N |
| Hotel → Reviews | 1:N |
| Restaurant → Reviews | 1:N |
| Trip → UserHistory | 1:N |
| TouristPlace → UserHistory | 1:N |
