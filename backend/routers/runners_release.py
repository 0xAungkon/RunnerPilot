from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, TypedDict

import urllib.request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from inc.auth import AuthorizedUser, authorized_user
from inc.utils.meta import get_meta as _get_meta, set_meta as _set_meta
from inc.config import settings
from inc.utils.release_helpers import  _now_utc_iso,_is_cache_fresh, _read_cache,_write_cache,_fetch_github_releases,_transform,_version_already_downloaded,_find_release_by_version,_get_download_filename,_download_with_progress

router = APIRouter()

CACHE_FILE = os.path.join(settings.VOLUME_PATH, "runner-release.json")
RUNNERS_DIR = os.path.join(settings.VOLUME_PATH, "runners", "releases")
META_LAST_PULL = "last_pulled_release"
TTL = timedelta(hours=1)
GITHUB_API = "https://api.github.com/repos/actions/runner/releases"


class ReleaseOut(BaseModel):
    published_at: Optional[str]
    name: Optional[str]
    size: Optional[int]  # size of selected asset (linux x64) if available
    download_url: Optional[str]
    html_url: Optional[str]
    is_pulled: bool  # whether this version has been downloaded
    is_linux_available: bool  # whether linux-x64 asset is available


class PullRunnerIn(BaseModel):
    version: str  # version name like "v2.329.0"


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
    """
    Download a specific runner release by version.
    Streams download progress as JSON lines.
    """
    version = payload.version.strip()

    # Check if version already exists
    if _version_already_downloaded(version):
        raise HTTPException(
            status_code=409,
            detail=f"Version {version} is already downloaded"
        )

    # Find the release in cache
    release = _find_release_by_version(version)
    if not release:
        raise HTTPException(
            status_code=404,
            detail=f"Version {version} not found in releases"
        )

    # Transform to get download URL
    transformed = _transform([release])
    if not transformed:
        raise HTTPException(
            status_code=500,
            detail="Failed to transform release data"
        )

    download_url = transformed[0].get("download_url")
    if not download_url:
        raise HTTPException(
            status_code=404,
            detail=f"No linux-x64 download URL found for version {version}"
        )

    # Extract filename and prepare filepath
    filename = _get_download_filename(download_url)
    filepath = os.path.join(RUNNERS_DIR, filename)

    # Return streaming response with download progress
    return StreamingResponse(
        _download_with_progress(download_url, filepath),
        media_type="application/x-ndjson"
    )


@router.delete("/runners/release/{version}")
async def delete_cached_release(version: str, user: AuthorizedUser = Depends(authorized_user)):
    """
    Delete a downloaded runner release by version.
    Removes all files matching the version name from the releases directory.
    """
    version = version.strip()
    
    try:
        os.makedirs(RUNNERS_DIR, exist_ok=True)
        files = os.listdir(RUNNERS_DIR)
        deleted_files = []

        for f in files:
            if f.startswith(version):
                filepath = os.path.join(RUNNERS_DIR, f)
                try:
                    os.remove(filepath)
                    deleted_files.append(f)
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to delete {f}: {str(e)}"
                    )

        if not deleted_files:
            return {"status": "ok", "message": f"No files found for version {version}"}

        return {
            "status": "ok",
            "message": f"Deleted {len(deleted_files)} file(s)",
            "version": version,
            "deleted_files": deleted_files
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
