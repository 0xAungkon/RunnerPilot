from fastapi import APIRouter, HTTPException
from inc.auth import AuthorizedUser, authorized_user
from pydantic import BaseModel
from typing import Any, List, Literal
from models import Meta
from inc.utils.meta_serialization import (
    serialize_meta_value as _serialize_meta_value,
    deserialize_meta_value as _deserialize_meta_value,
)
from fastapi import Depends

router = APIRouter()

MetaType = Literal["string", "int", "bool", "list", "json"]


class MetaIn(BaseModel):
    meta_key: str
    meta_value: Any
    meta_type: MetaType


class MetaOut(BaseModel):
    meta_key: str
    meta_value: Any
    meta_type: MetaType


def _serialize_value(value: Any, meta_type: MetaType) -> str:
    try:
        return _serialize_meta_value(value, meta_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


def _deserialize_value(raw: str, meta_type: MetaType) -> Any:
    return _deserialize_meta_value(raw, meta_type)


@router.post("/", response_model=MetaOut)
def create_meta(item: MetaIn, user: AuthorizedUser = Depends(authorized_user)):
    raw = _serialize_value(item.meta_value, item.meta_type)
    # Upsert: update if exists, else create
    existing = Meta.get_or_none(Meta.meta_key == item.meta_key)
    if existing:
        existing.meta_value = raw
        existing.meta_type = item.meta_type
        existing.save()
        row = existing
    else:
        try:
            row = Meta.create(meta_key=item.meta_key, meta_value=raw, meta_type=item.meta_type)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    return MetaOut(meta_key=row.meta_key, meta_value=_deserialize_value(row.meta_value, row.meta_type), meta_type=row.meta_type)


@router.get("/", response_model=List[MetaOut])
def list_meta(auth_user: AuthorizedUser = Depends(authorized_user)):
    rows = list(Meta.select().dicts())
    return [MetaOut(meta_key=r["meta_key"], meta_value=_deserialize_value(r["meta_value"], r["meta_type"]), meta_type=r["meta_type"]) for r in rows]


@router.get("/{key}", response_model=MetaOut)
def get_meta(key: str, user: AuthorizedUser = Depends(authorized_user)):
    row = Meta.get_or_none(Meta.meta_key == key)
    if not row:
        raise HTTPException(status_code=404, detail="Meta not found")
    return MetaOut(meta_key=row.meta_key, meta_value=_deserialize_value(row.meta_value, row.meta_type), meta_type=row.meta_type)
