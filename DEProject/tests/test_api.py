import pytest

from city_api.app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


@pytest.fixture
def city_payload():
    return {
        "city_name": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "temperature": 32.5,
        "humidity": 65,
        "weather_condition": "Sunny",
    }


def test_create_and_get_city(client, city_payload):
    response = client.post("/cities", json=city_payload)
    assert response.status_code == 201
    city = response.get_json()
    assert city["city_name"] == "Hyderabad"
    assert "recorded_at" in city

    response = client.get(f"/cities/{city['city_id']}")
    assert response.status_code == 200
    assert response.get_json() == city


def test_list_filter_update_and_delete(client, city_payload):
    first = client.post("/cities", json=city_payload).get_json()
    second_payload = {**city_payload, "city_name": "Warangal", "temperature": 28}
    client.post("/cities", json=second_payload)

    assert len(client.get("/cities?state=Telangana").get_json()) == 2
    assert len(client.get("/cities?min_temperature=30").get_json()) == 1

    updated = {**city_payload, "temperature": 35}
    response = client.put(f"/cities/{first['city_id']}", json=updated)
    assert response.status_code == 200
    assert response.get_json()["temperature"] == 35

    assert client.delete(f"/cities/{first['city_id']}").status_code == 200
    assert client.get(f"/cities/{first['city_id']}").status_code == 404


def test_validation_and_missing_records(client, city_payload):
    invalid = {**city_payload, "humidity": 101}
    response = client.post("/cities", json=invalid)
    assert response.status_code == 400
    assert response.get_json()["details"]["humidity"]

    assert client.post("/cities", json={}).status_code == 400
    assert client.get("/cities/999").status_code == 404
    assert client.delete("/cities/999").status_code == 404
    assert client.get("/cities?min_temperature=hot").status_code == 400


def test_statistics(client, city_payload):
    client.post("/cities", json=city_payload)
    client.post("/cities", json={**city_payload, "city_name": "Delhi", "temperature": 38})
    stats = client.get("/statistics")
    assert stats.status_code == 200
    assert stats.get_json() == {
        "total_cities": 2,
        "average_temperature": 35.25,
        "maximum_temperature": 38.0,
        "minimum_temperature": 32.5,
    }
