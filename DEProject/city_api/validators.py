from typing import Any


REQUIRED_FIELDS = (
    "city_name",
    "state",
    "country",
    "temperature",
    "humidity",
    "weather_condition",
)
TEXT_FIELDS = ("city_name", "state", "country", "weather_condition")


def validate_city(data: Any, partial: bool = False) -> dict[str, str]:
    if not isinstance(data, dict):
        return {"request": "JSON body must be an object."}

    errors: dict[str, str] = {}
    fields_to_check = data.keys() if partial else REQUIRED_FIELDS

    if not partial:
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        for field in missing:
            errors[field] = "This field is required."

    for field in fields_to_check:
        if field not in data:
            continue
        value = data[field]
        if field in TEXT_FIELDS and (not isinstance(value, str) or not value.strip()):
            errors[field] = "Must be a non-empty string."
        elif field == "temperature":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors[field] = "Must be numeric."
        elif field == "humidity":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors[field] = "Must be numeric."
            elif not 0 <= value <= 100:
                errors[field] = "Must be between 0 and 100."

    if partial and not any(field in data for field in REQUIRED_FIELDS):
        errors["request"] = "At least one city field is required."
    return errors
