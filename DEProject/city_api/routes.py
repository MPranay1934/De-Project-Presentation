import sqlite3
from flask import Blueprint, current_app, jsonify, request

from .database import get_connection
from .models import CITY_FIELDS, current_timestamp, row_to_dict
from .validators import validate_city


cities_bp = Blueprint("cities", __name__)


def _database_path():
    return current_app.config["DATABASE"]


def _error(message, status=400, details=None):
    body = {"error": message}
    if details:
        body["details"] = details
    return jsonify(body), status


@cities_bp.get("/cities")
def list_cities():
    state = request.args.get("state")
    minimum_temperature = request.args.get("min_temperature")
    query = "SELECT * FROM cities"
    conditions = []
    parameters = []

    if state is not None:
        conditions.append("state = ?")
        parameters.append(state)
    if minimum_temperature is not None:
        try:
            minimum_temperature = float(minimum_temperature)
        except ValueError:
            return _error("min_temperature must be numeric.")
        conditions.append("temperature >= ?")
        parameters.append(minimum_temperature)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY city_id"

    with get_connection(_database_path()) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return jsonify([row_to_dict(row) for row in rows])


@cities_bp.post("/cities")
def create_city():
    data = request.get_json(silent=True)
    errors = validate_city(data)
    if errors:
        return _error("Invalid city data.", details=errors)

    values = [data[field].strip() if isinstance(data[field], str) else data[field] for field in CITY_FIELDS]
    with get_connection(_database_path()) as connection:
        cursor = connection.execute(
            "INSERT INTO cities (city_name, state, country, temperature, humidity, weather_condition, recorded_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [*values, current_timestamp()],
        )
        city = connection.execute("SELECT * FROM cities WHERE city_id = ?", (cursor.lastrowid,)).fetchone()
        connection.commit()
    return jsonify(row_to_dict(city)), 201


@cities_bp.get("/cities/<int:city_id>")
def get_city(city_id):
    with get_connection(_database_path()) as connection:
        city = connection.execute("SELECT * FROM cities WHERE city_id = ?", (city_id,)).fetchone()
    if city is None:
        return _error("City not found.", 404)
    return jsonify(row_to_dict(city))


@cities_bp.put("/cities/<int:city_id>")
def update_city(city_id):
    data = request.get_json(silent=True)
    errors = validate_city(data, partial=True)
    if errors:
        return _error("Invalid city data.", details=errors)

    with get_connection(_database_path()) as connection:
        existing = connection.execute("SELECT * FROM cities WHERE city_id = ?", (city_id,)).fetchone()
        if existing is None:
            return _error("City not found.", 404)
        updated = {field: existing[field] for field in CITY_FIELDS}
        updated.update({field: data[field] for field in data if field in CITY_FIELDS})
        errors = validate_city(updated)
        if errors:
            return _error("Invalid city data.", details=errors)
        assignments = ", ".join(f"{field} = ?" for field in CITY_FIELDS)
        connection.execute(
            f"UPDATE cities SET {assignments}, recorded_at = ? WHERE city_id = ?",
            [updated[field].strip() if isinstance(updated[field], str) else updated[field] for field in CITY_FIELDS]
            + [current_timestamp(), city_id],
        )
        city = connection.execute("SELECT * FROM cities WHERE city_id = ?", (city_id,)).fetchone()
        connection.commit()
    return jsonify(row_to_dict(city))


@cities_bp.delete("/cities/<int:city_id>")
def delete_city(city_id):
    with get_connection(_database_path()) as connection:
        result = connection.execute("DELETE FROM cities WHERE city_id = ?", (city_id,))
        connection.commit()
    if result.rowcount == 0:
        return _error("City not found.", 404)
    return jsonify({"message": "City deleted successfully."})


@cities_bp.get("/statistics")
def statistics():
    with get_connection(_database_path()) as connection:
        stats = connection.execute(
            "SELECT COUNT(*) AS total_cities, AVG(temperature) AS average_temperature, "
            "MAX(temperature) AS maximum_temperature, MIN(temperature) AS minimum_temperature FROM cities"
        ).fetchone()
    result = row_to_dict(stats)
    if result["average_temperature"] is not None:
        result["average_temperature"] = round(result["average_temperature"], 2)
    return jsonify(result)
