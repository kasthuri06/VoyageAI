"""
Unit tests for route optimization algorithms.
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.route_optimizer import (
    haversine_distance,
    build_complete_graph,
    dijkstra,
    astar,
    nearest_neighbour_tsp,
    _algorithm_fallback,
)

MUMBAI = (18.9220, 72.8347)
GOA    = (15.4925, 73.7733)
PUNE   = (18.5204, 73.8567)


def test_haversine_distance():
    dist = haversine_distance(MUMBAI, GOA)
    assert 350 < dist < 450  # roughly 392 km straight line


def test_haversine_same_point():
    assert haversine_distance(MUMBAI, MUMBAI) == pytest.approx(0, abs=0.1)


def test_build_complete_graph():
    places = [
        {"latitude": MUMBAI[0], "longitude": MUMBAI[1]},
        {"latitude": GOA[0],    "longitude": GOA[1]},
        {"latitude": PUNE[0],   "longitude": PUNE[1]},
    ]
    graph = build_complete_graph(places)
    assert len(graph) == 3
    assert len(graph[0]) == 2  # connected to 2 others


def test_dijkstra_finds_path():
    places = [
        {"latitude": MUMBAI[0], "longitude": MUMBAI[1]},
        {"latitude": PUNE[0],   "longitude": PUNE[1]},
        {"latitude": GOA[0],    "longitude": GOA[1]},
    ]
    graph = build_complete_graph(places)
    dist, path = dijkstra(graph, start=0, end=2)
    assert dist > 0
    assert path[0] == 0
    assert path[-1] == 2


def test_astar_finds_path():
    places = [
        {"latitude": MUMBAI[0], "longitude": MUMBAI[1]},
        {"latitude": PUNE[0],   "longitude": PUNE[1]},
        {"latitude": GOA[0],    "longitude": GOA[1]},
    ]
    graph = build_complete_graph(places)
    coords = [(p["latitude"], p["longitude"]) for p in places]
    dist, path = astar(graph, coords, start=0, end=2)
    assert dist > 0
    assert path[0] == 0
    assert path[-1] == 2


def test_nearest_neighbour_tsp_ordering():
    places = [
        {"name": "Mumbai", "latitude": MUMBAI[0], "longitude": MUMBAI[1]},
        {"name": "Goa",    "latitude": GOA[0],    "longitude": GOA[1]},
        {"name": "Pune",   "latitude": PUNE[0],   "longitude": PUNE[1]},
    ]
    ordered = nearest_neighbour_tsp(places)
    assert len(ordered) == 3
    # Starting from Mumbai, Pune should come before Goa (closer)
    assert ordered[0]["name"] == "Mumbai"
    assert ordered[1]["name"] == "Pune"


def test_algorithm_fallback():
    result = _algorithm_fallback(MUMBAI, GOA)
    assert result["source"] == "algorithm"
    assert result["distance_km"] > 0
    assert result["duration_minutes"] > 0


def test_nearest_neighbour_single():
    places = [{"name": "Mumbai", "latitude": MUMBAI[0], "longitude": MUMBAI[1]}]
    ordered = nearest_neighbour_tsp(places)
    assert len(ordered) == 1
