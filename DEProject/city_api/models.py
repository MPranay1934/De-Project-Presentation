from datetime import datetime, timezone
import sqlite3
from typing import Any


CITY_FIELDS = (
    "city_name",
    "state",
    "country",
    "temperature",
    "humidity",
    "weather_condition",
)


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
