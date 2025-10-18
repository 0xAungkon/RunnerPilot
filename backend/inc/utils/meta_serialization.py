import json
from typing import Any


def serialize_meta_value(value: Any, meta_type: str) -> str:
    if meta_type == "string":
        return str(value)
    if meta_type == "int":
        return str(int(value))
    if meta_type == "bool":
        if isinstance(value, bool):
            return "true" if value else "false"
        s = str(value).lower()
        if s in ["true", "1", "yes", "y"]:
            return "true"
        if s in ["false", "0", "no", "n"]:
            return "false"
        raise ValueError("meta_value must be a boolean")
    if meta_type in ("list", "json"):
        return json.dumps(value)
    raise ValueError("Invalid meta_type")


def deserialize_meta_value(raw: str, meta_type: str) -> Any:
    if meta_type == "string":
        return raw
    if meta_type == "int":
        return int(raw)
    if meta_type == "bool":
        return raw.lower() in ("true", "1", "yes", "y")
    if meta_type in ("list", "json"):
        return json.loads(raw) if raw else None
    return raw
