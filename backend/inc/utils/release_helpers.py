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

# -------- Constants ---------
CACHE_FILE = os.path.join(settings.VOLUME_PATH, "runner-release.json")
RUNNERS_DIR = os.path.join(settings.VOLUME_PATH, "runners", "releases")
META_LAST_PULL = "last_pulled_release"
TTL = timedelta(hours=1)
GITHUB_API = "https://api.github.com/repos/actions/runner/releases"



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


def _fetch_and_cache_releases() -> list[dict[str, Any]]:
    """
    Centralized function to fetch releases from GitHub, cache them, and update metadata.
    Returns the raw release data from GitHub API.
    """
    raw = _fetch_github_releases()
    _write_cache(raw)
    _set_meta(META_LAST_PULL, _now_utc_iso(), meta_type="string")
    return raw


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
        version_name = r.get("name", "")
        is_pulled = _version_already_downloaded(version_name)
        is_linux_available = dl is not None
        out.append(
            {
                "published_at": r.get("published_at"),
                "name": version_name,
                "size": size,
                "download_url": dl,
                "html_url": r.get("html_url"),
                "is_pulled": is_pulled,
                "is_linux_available": is_linux_available,
            }
        )
    return out


def _find_release_by_version(version: str) -> Optional[dict[str, Any]]:
    """Find a release in cache by version name."""
    try:
        data = _read_cache()
        for r in data:
            if r.get("name") == version:
                return r
    except Exception:
        pass
    return None


def _get_download_filename(url: str) -> str:
    """Extract filename from download URL."""
    return url.split("/")[-1]


def _version_already_downloaded(version: str) -> bool:
    """Check if a version is already downloaded."""
    os.makedirs(RUNNERS_DIR, exist_ok=True)
    # List all files in the releases directory
    try:
        files = os.listdir(RUNNERS_DIR)
        # Check if any file starts with the version name
        for f in files:
            if f.startswith(version):
                return True
    except Exception:
        pass
    return False


def _download_with_progress(url: str, filepath: str) -> Any:
    """Generator that yields download progress as JSON lines."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 8192

            # Create parent directories
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Calculate percentage
                    if total_size > 0:
                        percentage = int((downloaded / total_size) * 100)
                    else:
                        percentage = 0

                    # Yield progress as JSON
                    progress_json = json.dumps({
                        "status": "downloading",
                        "percentage": percentage,
                        "downloaded": downloaded,
                        "total": total_size,
                    })
                    yield f"{progress_json}\n"

            # Yield completion message
            completion_json = json.dumps({
                "status": "completed",
                "percentage": 100,
                "message": "Download completed successfully",
            })
            yield f"{completion_json}\n"

    except Exception as e:
        error_json = json.dumps({
            "status": "error",
            "message": str(e),
        })
        yield f"{error_json}\n"


# -------- Routes ----------