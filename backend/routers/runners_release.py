from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, TypedDict

import urllib.request
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from inc.auth import AuthorizedUser, authorized_user
from inc.utils.meta import get_meta as _get_meta, set_meta as _set_meta
from inc.config import settings

router = APIRouter()

CACHE_FILE = os.path.join(settings.VOLUME_PATH, "runner-release.json")
META_LAST_PULL = "last_pulled_release"
TTL = timedelta(hours=1)
GITHUB_API = "https://api.github.com/repos/actions/runner/releases"


class ReleaseOut(BaseModel):
    published_at: Optional[str]
    name: Optional[str]
    size: Optional[int]  # size of selected asset (linux x64) if available
    download_url: Optional[str]
    html_url: Optional[str]


class PullRunnerIn(BaseModel):
    id: int
    description: Optional[str] = "pull runner"


# -------- Helpers ---------

def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_cache_fresh() -> bool:
    # meta time check
    last_pull_val = _get_meta(META_LAST_PULL)
    if last_pull_val:
        try:
            last_dt = datetime.fromisoformat(str(last_pull_val))
        except Exception:
            last_dt = None
        if isinstance(last_dt, datetime):
            if datetime.now(timezone.utc) - last_dt < TTL:
                # If TTL not expired, also ensure file exists
                return os.path.exists(CACHE_FILE)
    return False


def _read_cache() -> list[Any]:
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read cache: {e}")


def _write_cache(data: list[Any]) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _fetch_github_releases() -> list[dict[str, Any]]:
    try:
        with urllib.request.urlopen(GITHUB_API) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail="GitHub API error")
            body = resp.read()
            return json.loads(body.decode("utf-8"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch releases: {e}")


def _pick_linux_x64_asset(assets: list[dict[str, Any]]) -> tuple[Optional[str], Optional[int]]:
    if not assets:
        return None, None
    for a in assets:
        url = a.get("browser_download_url") or ""
        if "actions-runner-linux-x64" in url:
            return url, a.get("size")
    # If exact x64 not present, return first linux asset (best effort)
    for a in assets:
        url = a.get("browser_download_url") or ""
        if "actions-runner-linux" in url:
            return url, a.get("size")
    return None, None


def _transform(releases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in releases:
        assets = r.get("assets") or []
        dl, size = _pick_linux_x64_asset(assets)
        out.append(
            {
                "published_at": r.get("published_at"),
                "name": r.get("name"),
                "size": size,
                "download_url": dl,
                "html_url": r.get("html_url"),
            }
        )
    return out


# -------- Routes ----------

@router.get("/runners/release", response_model=List[ReleaseOut])
async def get_releases(user: AuthorizedUser = Depends(authorized_user)):
    # 1-2: check cache TTL using meta and file
    if _is_cache_fresh():
        raw = _read_cache()
        return _transform(raw)

    # 3: fetch from GitHub
    raw = _fetch_github_releases()

    # 4: save and update meta
    _write_cache(raw)
    _set_meta(META_LAST_PULL, _now_utc_iso(), meta_type="string")

    # 5: transform
    return _transform(raw)


@router.post("/runners/release")
async def pull_runner(payload: PullRunnerIn, user: AuthorizedUser = Depends(authorized_user)):
    # For now, just acknowledge the intent to pull a runner by id.
    # Future: implement actual download/install based on id selection.
    return {"status": "ok", "message": "pull runner requested", "id": payload.id}


@router.delete("/runners/release/{id}")
async def delete_cached_release(id: int, user: AuthorizedUser = Depends(authorized_user)):
    # Here, interpret delete as removing cache or specific entry from cache
    # Since GitHub release list is authoritative, we'll clear cache if it contains the id
    try:
        data = _read_cache()
        if not data:
            return {"status": "ok", "message": "nothing to delete"}
        new_data = [r for r in data if int(r.get("id", -1)) != id]
        if len(new_data) == len(data):
            # id not found: no-op
            return {"status": "ok", "message": "id not found in cache"}
        _write_cache(new_data)
        # keep last_pulled timestamp as-is
        return {"status": "ok", "message": "deleted from cache", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
