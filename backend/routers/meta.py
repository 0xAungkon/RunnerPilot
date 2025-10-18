from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List, Literal, Optional
from models import Meta
import json

router = APIRouter()

MetaType = Literal["string", "int", "bool", "list", "json"]


class MetaIn(BaseModel):
    meta_key: str
    meta_value: Any
    meta_type: MetaType


class MetaOut(BaseModel):
    id: int
    meta_key: str
    meta_value: Any
    meta_type: MetaType


# helper to serialize meta_value according to meta_type

def _serialize_value(value: Any, meta_type: MetaType) -> str:
    if meta_type == "string":
        return str(value)
    if meta_type == "int":
        try:
            return str(int(value))
        except Exception:
            raise HTTPException(status_code=422, detail="meta_value must be an integer")
    if meta_type == "bool":
        if isinstance(value, bool):
            return "true" if value else "false"
        s = str(value).lower()
        if s in ["true", "1", "yes", "y"]:
            return "true"
        if s in ["false", "0", "no", "n"]:
            return "false"
        raise HTTPException(status_code=422, detail="meta_value must be a boolean")
    if meta_type in ("list", "json"):
        try:
            return json.dumps(value)
        except Exception:
            raise HTTPException(status_code=422, detail="meta_value must be JSON-serializable")
    raise HTTPException(status_code=422, detail="Invalid meta_type")


def _deserialize_value(raw: str, meta_type: MetaType) -> Any:
    if meta_type == "string":
        return raw
    if meta_type == "int":
        return int(raw)
    if meta_type == "bool":
        return raw.lower() in ("true", "1", "yes", "y")
    if meta_type in ("list", "json"):
        return json.loads(raw) if raw else None
    return raw


@router.post("/", response_model=MetaOut)
def create_meta(item: MetaIn):
    raw = _serialize_value(item.meta_value, item.meta_type)
    try:
        row = Meta.create(meta_key=item.meta_key, meta_value=raw, meta_type=item.meta_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MetaOut(id=row.id, meta_key=row.meta_key, meta_value=_deserialize_value(row.meta_value, row.meta_type), meta_type=row.meta_type)


@router.get("/", response_model=List[MetaOut])
def list_meta():
    rows = list(Meta.select().dicts())
    return [MetaOut(id=r["id"], meta_key=r["meta_key"], meta_value=_deserialize_value(r["meta_value"], r["meta_type"]), meta_type=r["meta_type"]) for r in rows]


@router.get("/{key}", response_model=MetaOut)
def get_meta(key: str):
    row = Meta.get_or_none(Meta.meta_key == key)
    if not row:
        raise HTTPException(status_code=404, detail="Meta not found")
    return MetaOut(id=row.id, meta_key=row.meta_key, meta_value=_deserialize_value(row.meta_value, row.meta_type), meta_type=row.meta_type)
