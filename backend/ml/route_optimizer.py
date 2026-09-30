"""
Voyage AI – Route Optimization Module

Supports:
  1. Dijkstra Algorithm  (pure Python, no API needed)
  2. A* Algorithm        (pure Python, heuristic-guided)
  3. Google Directions API
  4. OpenRouteService API

Switching between modes is done via config.ROUTING_MODE:
  "algorithm" → Dijkstra / A*
  "google"    → Google Directions API
  "ors"       → OpenRouteService API
"""
import math
import heapq
import logging
import asyncio
from typing import List, Dict, Tuple, Optional, Any

import httpx
from geopy.distance import geodesic

from config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Coordinate type alias
# ---------------------------------------------------------------------------
Coord = Tuple[float, float]  # (latitude, longitude)


# ===========================================================================
# Graph construction helpers
# ===========================================================================

def haversine_distance(a: Coord, b: Coord) -> float:
    """Return the great-circle distance in kilometers between two lat/lon points."""
    return geodesic(a, b).km


def build_complete_graph(places: List[Dict]) -> Dict[int, List[Tuple[float, int]]]:
    """
    Build a complete undirected weighted graph from a list of places.
    Each place must have 'latitude' and 'longitude' keys.
    Edge weight = haversine distance in km.

    Returns adjacency list: {node_index: [(distance_km, neighbour_index), ...]}
    """
    n = len(places)
    graph: Dict[int, List[Tuple[float, int]]] = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine_distance(
                (places[i]["latitude"], places[i]["longitude"]),
                (places[j]["latitude"], places[j]["longitude"]),
            )
            graph[i].append((d, j))
            graph[j].append((d, i))
    return graph


# ===========================================================================
# Algorithm 1: Dijkstra's Shortest Path
# ===========================================================================

def dijkstra(graph: Dict[int, List[Tuple[float, int]]], start: int, end: int) -> Tuple[float, List[int]]:
    """
    Dijkstra's algorithm for single-source shortest path.

    Returns:
        (total_distance_km, path_as_node_indices)
    """
    n = len(graph)
    dist = [float("inf")] * n
    dist[start] = 0.0
    prev = [-1] * n
    visited = set()
    heap = [(0.0, start)]

    while heap:
        current_dist, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == end:
            break
        for weight, v in graph[u]:
            new_dist = current_dist + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))

    # Reconstruct path
    path = []
    node = end
    while node != -1:
        path.append(node)
        node = prev[node]
    path.reverse()

    if path[0] != start:
        return float("inf"), []
    return dist[end], path


# ===========================================================================
# Algorithm 2: A* Algorithm
# ===========================================================================

def astar(
    graph: Dict[int, List[Tuple[float, int]]],
    coords: List[Coord],
    start: int,
    end: int,
) -> Tuple[float, List[int]]:
    """
    A* algorithm using haversine distance as the heuristic.

    Args:
        graph:  Adjacency list
        coords: List of (lat, lon) for each node
        start:  Start node index
        end:    End node index

    Returns:
        (total_distance_km, path_as_node_indices)
    """
    n = len(graph)
    g_score = [float("inf")] * n
    g_score[start] = 0.0
    f_score = [float("inf")] * n
    f_score[start] = haversine_distance(coords[start], coords[end])
    prev = [-1] * n
    open_set = [(f_score[start], start)]
    closed_set = set()

    while open_set:
        _, u = heapq.heappop(open_set)
        if u == end:
            break
        if u in closed_set:
            continue
        closed_set.add(u)
        for weight, v in graph[u]:
            tentative_g = g_score[u] + weight
            if tentative_g < g_score[v]:
                g_score[v] = tentative_g
                f_score[v] = tentative_g + haversine_distance(coords[v], coords[end])
                prev[v] = u
                heapq.heappush(open_set, (f_score[v], v))

    path = []
    node = end
    while node != -1:
        path.append(node)
        node = prev[node]
    path.reverse()

    if not path or path[0] != start:
        return float("inf"), []
    return g_score[end], path


# ===========================================================================
# Nearest-Neighbour TSP approximation (for multi-stop routes)
# ===========================================================================

def nearest_neighbour_tsp(places: List[Dict]) -> List[Dict]:
    """
    Greedy nearest-neighbour approximation for the Travelling Salesman Problem.
    Used to order the recommended places in an optimized visitation sequence.

    Returns the list of places reordered for an efficient route.
    """
    if len(places) <= 1:
        return places

    n = len(places)
    visited = [False] * n
    route = [0]
    visited[0] = True

    for _ in range(n - 1):
        last = route[-1]
        best_dist = float("inf")
        best_next = -1
        for j in range(n):
            if not visited[j]:
                d = haversine_distance(
                    (places[last]["latitude"], places[last]["longitude"]),
                    (places[j]["latitude"], places[j]["longitude"]),
                )
                if d < best_dist:
                    best_dist = d
                    best_next = j
        if best_next >= 0:
            route.append(best_next)
            visited[best_next] = True

    return [places[i] for i in route]


# ===========================================================================
# API-based Routing
# ===========================================================================

async def get_google_route(
    origin: Coord,
    destination: Coord,
    waypoints: Optional[List[Coord]] = None,
    mode: str = "driving",
) -> Dict[str, Any]:
    """
    Fetch route from Google Directions API.

    Returns dict with distance_km, duration_minutes, polyline, steps.
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        logger.warning("Google Maps API key not configured, falling back to algorithm")
        return _algorithm_fallback(origin, destination)

    origin_str = f"{origin[0]},{origin[1]}"
    dest_str = f"{destination[0]},{destination[1]}"
    waypoints_str = ""
    if waypoints:
        wp_list = "|".join(f"{w[0]},{w[1]}" for w in waypoints)
        waypoints_str = f"&waypoints=optimize:true|{wp_list}"

    url = (
        f"https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={origin_str}&destination={dest_str}"
        f"{waypoints_str}&mode={mode}"
        f"&key={settings.GOOGLE_MAPS_API_KEY}"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            data = resp.json()

        if data.get("status") != "OK":
            logger.warning(f"Google API returned status: {data.get('status')}")
            return _algorithm_fallback(origin, destination)

        route = data["routes"][0]
        leg = route["legs"][0]
        return {
            "source": "google",
            "distance_km": leg["distance"]["value"] / 1000,
            "duration_minutes": leg["duration"]["value"] / 60,
            "polyline": route["overview_polyline"]["points"],
            "steps": [
                {
                    "instruction": s["html_instructions"],
                    "distance_km": s["distance"]["value"] / 1000,
                    "duration_minutes": s["duration"]["value"] / 60,
                }
                for s in leg["steps"]
            ],
        }
    except Exception as e:
        logger.error(f"Google Maps API error: {e}")
        return _algorithm_fallback(origin, destination)


async def get_ors_route(
    origin: Coord,
    destination: Coord,
    profile: str = "driving-car",
) -> Dict[str, Any]:
    """
    Fetch route from OpenRouteService API.
    """
    if not settings.OPENROUTESERVICE_API_KEY:
        logger.warning("ORS API key not configured, falling back to algorithm")
        return _algorithm_fallback(origin, destination)

    url = "https://api.openrouteservice.org/v2/directions/" + profile
    headers = {
        "Authorization": settings.OPENROUTESERVICE_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "coordinates": [
            [origin[1], origin[0]],      # ORS uses [lon, lat]
            [destination[1], destination[0]],
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=body, headers=headers)
            data = resp.json()

        segment = data["routes"][0]["segments"][0]
        return {
            "source": "ors",
            "distance_km": segment["distance"] / 1000,
            "duration_minutes": segment["duration"] / 60,
            "polyline": data["routes"][0].get("geometry"),
            "steps": [
                {
                    "instruction": s["instruction"],
                    "distance_km": s["distance"] / 1000,
                    "duration_minutes": s["duration"] / 60,
                }
                for s in segment["steps"]
            ],
        }
    except Exception as e:
        logger.error(f"ORS API error: {e}")
        return _algorithm_fallback(origin, destination)


def _algorithm_fallback(origin: Coord, destination: Coord) -> Dict[str, Any]:
    """
    Simple straight-line distance fallback when APIs are unavailable.
    Estimates road distance as 1.4× the haversine distance.
    """
    straight = haversine_distance(origin, destination)
    road_est = straight * 1.4
    speed_kmh = 50
    return {
        "source": "algorithm",
        "distance_km": round(road_est, 2),
        "duration_minutes": round((road_est / speed_kmh) * 60, 1),
        "polyline": None,
        "steps": [],
    }


# ===========================================================================
# Main Router – dispatches based on settings.ROUTING_MODE
# ===========================================================================

async def optimize_route(
    places: List[Dict],
    transport_mode: str = "car",
) -> Dict[str, Any]:
    """
    Orchestrate route optimization for a list of tourist places.

    Returns:
        {
            "ordered_places": [...],
            "total_distance_km": float,
            "total_duration_minutes": float,
            "legs": [{source, distance_km, duration_minutes, ...}, ...]
        }
    """
    if len(places) == 0:
        return {"ordered_places": [], "total_distance_km": 0, "total_duration_minutes": 0, "legs": []}

    if len(places) == 1:
        return {"ordered_places": places, "total_distance_km": 0, "total_duration_minutes": 0, "legs": []}

    # Step 1: Reorder places using nearest-neighbour TSP
    ordered = nearest_neighbour_tsp(places)

    mode = settings.ROUTING_MODE
    google_mode_map = {"car": "driving", "bike": "bicycling", "walk": "walking", "public": "transit"}
    ors_profile_map = {"car": "driving-car", "bike": "cycling-regular", "walk": "foot-walking"}

    legs = []
    total_dist = 0.0
    total_dur = 0.0

    for i in range(len(ordered) - 1):
        origin = (ordered[i]["latitude"], ordered[i]["longitude"])
        dest = (ordered[i + 1]["latitude"], ordered[i + 1]["longitude"])

        if mode == "google":
            leg = await get_google_route(origin, dest, mode=google_mode_map.get(transport_mode, "driving"))
        elif mode == "ors":
            leg = await get_ors_route(origin, dest, profile=ors_profile_map.get(transport_mode, "driving-car"))
        else:
            leg = _algorithm_fallback(origin, dest)

        legs.append(leg)
        total_dist += leg["distance_km"]
        total_dur += leg["duration_minutes"]

    return {
        "ordered_places": ordered,
        "total_distance_km": round(total_dist, 2),
        "total_duration_minutes": round(total_dur, 1),
        "legs": legs,
    }
