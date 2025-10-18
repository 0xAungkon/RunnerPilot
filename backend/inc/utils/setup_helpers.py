import json
import os
import urllib.request
from typing import Any, Generator
from inc.config import settings
from inc.utils.prerequisites import check_prerequisites

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


def _get_latest_release() -> dict[str, Any] | None:
    """Fetch the latest runner release from GitHub API cache or live."""
    from inc.utils.release_helpers import _read_cache, _is_cache_fresh, _fetch_and_cache_releases, _transform
    
    # Try to read from cache first
    try:
        if _is_cache_fresh():
            cached = _read_cache()
            if cached:
                transformed = _transform(cached)
                if transformed:
                    return transformed[0]  # Return latest (first in list)
    except Exception:
        pass
    
    # If no cache, fetch and cache from GitHub
    try:
        raw = _fetch_and_cache_releases()
        transformed = _transform(raw)
        if transformed:
            return transformed[0]
    except Exception:
        pass
    
    return None


def _download_with_progress_streaming(url: str, filepath: str) -> Generator[str, None, None]:
    """Generator that yields download progress as JSON lines for streaming."""
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
                        "action": "pulling latest action runner",
                        "percentage": percentage,
                        "downloaded": downloaded,
                        "total": total_size,
                    })
                    yield f"{progress_json}\n"

            # Yield completion message
            completion_json = json.dumps({
                "action": "pulling latest action runner",
                "percentage": 100,
                "message": "Runner image downloaded successfully",
            })
            yield f"{completion_json}\n"

    except Exception as e:
        error_json = json.dumps({
            "action": "error",
            "message": f"Failed to download runner: {str(e)}",
        })
        yield f"{error_json}\n"


def _pull_ubuntu_docker_image() -> Generator[str, None, None]:
    """Generator that pulls ubuntu:latest Docker image and yields progress."""
    if not DOCKER_AVAILABLE:
        error_json = json.dumps({
            "action": "error",
            "message": "Docker is not available",
        })
        yield f"{error_json}\n"
        return
    
    try:
        client = docker.from_env()
        
        # Yield start message
        start_json = json.dumps({
            "action": "pulling ubuntu docker image",
            "status": "starting",
        })
        yield f"{start_json}\n"
        
        # Pull the image with streaming
        for line in client.api.pull("ubuntu:latest", stream=True, decode=True):
            # Extract relevant info from docker API response
            if "status" in line:
                status = line.get("status", "")
                progress = line.get("progress", "")
                
                progress_json = json.dumps({
                    "action": "pulling ubuntu docker image",
                    "status": status,
                    "progress": progress,
                })
                yield f"{progress_json}\n"
        
        # Yield completion message
        completion_json = json.dumps({
            "action": "pulling ubuntu docker image",
            "status": "completed",
            "message": "Ubuntu image pulled successfully",
        })
        yield f"{completion_json}\n"
        
    except Exception as e:
        error_json = json.dumps({
            "action": "error",
            "message": f"Failed to pull ubuntu image: {str(e)}",
        })
        yield f"{error_json}\n"


def setup_streaming_generator() -> Generator[str, None, None]:
    """Main setup generator that validates and downloads everything with streaming."""
    
    # Step 1: Check prerequisites
    prereq_result = check_prerequisites()
    
    if not prereq_result.status:
        # If global status is False, return error
        error_json = json.dumps({
            "action": "error",
            "message": "Prerequisites not met. Please ensure all mandatory checks pass.",
            "checks": [check.model_dump() for check in prereq_result.checks],
        })
        yield f"{error_json}\n"
        return
    
    # Yield success for prerequisites
    prereq_json = json.dumps({
        "action": "prerequisites check",
        "status": "passed",
        "message": "All prerequisites met",
    })
    yield f"{prereq_json}\n"
    
    # Step 2: Download latest runner image
    latest_release = _get_latest_release()
    if latest_release and latest_release.get("download_url"):
        runners_dir = os.path.join(settings.VOLUME_PATH, "runners", "releases")
        filename = latest_release["download_url"].split("/")[-1]
        filepath = os.path.join(runners_dir, filename)
        
        yield from _download_with_progress_streaming(latest_release["download_url"], filepath)
    else:
        error_json = json.dumps({
            "action": "error",
            "message": "Could not find latest runner release",
        })
        yield f"{error_json}\n"
        return
    
    # Step 3: Pull ubuntu Docker image
    yield from _pull_ubuntu_docker_image()
    
    # Step 4: Mark setup as complete
    from inc.utils.meta import set_meta
    set_meta("is_setup", True, meta_type="bool")
    
    final_json = json.dumps({
        "action": "setup",
        "status": "completed",
        "message": "System setup completed successfully",
    })
    yield f"{final_json}\n"
