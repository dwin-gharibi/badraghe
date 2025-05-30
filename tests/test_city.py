import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)

def test_get_all_unique_cities_success():
    response = client.get("/cities/")
    assert response.status_code == 200
    assert "cities" in response.json()
    assert isinstance(response.json()["cities"], list)

def test_get_departure_cities_no_query():
    response = client.get("/cities/departure")
    assert response.status_code == 200
    assert "departure_cities" in response.json()
    assert isinstance(response.json()["departure_cities"], list)

def test_get_departure_cities_with_query():
    response = client.get("/cities/departure?q=New")
    assert response.status_code == 200
    assert "departure_cities" in response.json()
    assert isinstance(response.json()["departure_cities"], list)
    for city in response.json()["departure_cities"]:
        assert "new" in city.lower()

def test_get_departure_cities_with_query_no_match():
    response = client.get("/cities/departure?q=NonExistentCityXYZ")
    assert response.status_code == 200
    assert response.json()["departure_cities"] == []

def test_get_arrival_cities_no_query():
    response = client.get("/cities/arrival")
    assert response.status_code == 200
    assert "arrival_cities" in response.json()
    assert isinstance(response.json()["arrival_cities"], list)

def test_get_arrival_cities_with_query():
    response = client.get("/cities/arrival?q=York")
    assert response.status_code == 200
    assert "arrival_cities" in response.json()
    assert isinstance(response.json()["arrival_cities"], list)
    for city in response.json()["arrival_cities"]:
        assert "york" in city.lower()

def test_get_arrival_cities_with_query_no_match():
    response = client.get("/cities/arrival?q=DoesNotExistCity")
    assert response.status_code == 200
    assert response.json()["arrival_cities"] == []

def test_departure_query_with_special_chars():
    response = client.get("/cities/departure?q=%")
    assert response.status_code == 200
    assert isinstance(response.json()["departure_cities"], list)

def test_arrival_query_case_insensitive():
    response_upper = client.get("/cities/arrival?q=PARIS")
    response_lower = client.get("/cities/arrival?q=paris")
    assert response_upper.status_code == 200
    assert response_lower.status_code == 200
    assert response_upper.json() == response_lower.json()

def test_city_endpoint_invalid_method():
    response = client.post("/cities/")
    assert response.status_code == 405
