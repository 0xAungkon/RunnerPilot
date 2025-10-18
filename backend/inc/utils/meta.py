from typing import Any
from models import Meta
from inc.db import db


def set_meta(key: str, value: Any, meta_type: str | None = None) -> None:
    """Set or update a meta value. If meta_type is not provided and the row exists,
    the existing meta_type will be preserved. If row doesn't exist and meta_type is missing,
    it will default to 'json' for non-scalars, 'string' for str, 'int' for int, and 'bool' for bool.
    """
    # Determine meta_type if not provided
    if meta_type is None:
        if isinstance(value, bool):
            meta_type = "bool"
        elif isinstance(value, int):
            meta_type = "int"
        elif isinstance(value, str):
            meta_type = "string"
        else:
            meta_type = "json"

    # Serialize similar to router logic
    from .serialization import serialize_meta_value  # type: ignore

    raw = serialize_meta_value(value, meta_type)

    with db.atomic():
        row = Meta.get_or_none(Meta.meta_key == key)
        if row is None:
            Meta.create(meta_key=key, meta_value=raw, meta_type=meta_type)
        else:
            row.meta_value = raw
            if meta_type:
                row.meta_type = meta_type
            row.save()


def get_meta(key: str) -> Any:
    from .serialization import deserialize_meta_value  # type: ignore

    row = Meta.get_or_none(Meta.meta_key == key)
    if row is None:
        return None
    return deserialize_meta_value(row.meta_value, row.meta_type)
