import json
import os
import urllib.request
import time
from typing import Any, Generator, Optional
from inc.config import settings
from inc.utils.prerequisites import check_prerequisites

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


def _is_ubuntu_image_available() -> bool:
    """Check if ubuntu:latest Docker image is available."""
    if not DOCKER_AVAILABLE:
        return False
    try:
        client = docker.from_env()
        images = client.images.list()
        for image in images:
            if image.tags:
                for tag in image.tags:
                    if "ubuntu" in tag and ("latest" in tag or tag.endswith("ubuntu")):
                        return True
        return False
    except Exception:
        return False


def _is_runner_binary_available_and_valid(expected_digest: Optional[str] = None) -> bool:
    """Check if runner binary/archive is available and matches digest if provided."""
    try:
        runners_dir = os.path.join(settings.VOLUME_PATH, "runner")
        if not os.path.exists(runners_dir):
            return False
        files = os.listdir(runners_dir)
        # Check if actions-runner tar.gz exists
        for f in files:
            if "actions-runner" in f and f.endswith(".tar.gz"):
                filepath = os.path.join(runners_dir, f)
                # If digest is provided, verify it
                if expected_digest:
                    from inc.utils.release_helpers import _verify_downloaded_file_digest
                    return _verify_downloaded_file_digest(filepath, expected_digest)
                # If no digest provided, just check file exists
                return True
        return False
    except Exception:
        return False


def _get_latest_release() -> dict[str, Any] | None:
    """Fetch the latest runner release from GitHub API cache or live with fallback."""
    from inc.utils.release_helpers import _read_cache, _is_cache_fresh, _fetch_with_fallback, _transform
    
    # Try to read from cache first if fresh
    try:
        if _is_cache_fresh():
            cached = _read_cache()
            if cached:
                transformed = _transform(cached)
                if transformed:
                    return transformed[0]  # Return latest (first in list)
    except Exception:
        pass
    
    # If no fresh cache, fetch from GitHub with fallback to expired cache
    try:
        raw = _fetch_with_fallback()
        transformed = _transform(raw)
        if transformed:
            return transformed[0]
    except Exception:
        pass
    
    return None


def _download_with_progress_streaming(url: str, filepath: str) -> Generator[str, None, None]:
    """Generator that yields download progress as JSON lines every 3 seconds."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 8192
            last_yield_time = time.time()

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

                    # Yield progress every 3 seconds or when download is complete
                    current_time = time.time()
                    if current_time - last_yield_time >= 3 or downloaded == total_size:
                        progress_json = json.dumps({
                            "action": "pulling latest action runner",
                            "percentage": percentage,
                            "downloaded": downloaded,
                            "total": total_size,
                        })
                        yield f"{progress_json}\n"
                        last_yield_time = current_time

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
    """Generator that pulls ubuntu:latest Docker image and yields progress every 3 seconds."""
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
        
        last_yield_time = time.time()
        
        # Pull the image with streaming
        for line in client.api.pull("ubuntu:latest", stream=True, decode=True):
            # Extract relevant info from docker API response
            if "status" in line:
                status = line.get("status", "")
                progress = line.get("progress", "")
                
                # Yield progress every 3 seconds or when pull is complete
                current_time = time.time()
                if current_time - last_yield_time >= 3 or status in ["Pull complete", "Digest:", "Status:"]:
                    progress_json = json.dumps({
                        "action": "pulling ubuntu docker image",
                        "status": status,
                        "progress": progress,
                    })
                    yield f"{progress_json}\n"
                    last_yield_time = current_time
        
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


def _build_docker_image() -> Generator[str, None, None]:
    """Generator that builds the GitHub runner Docker image and yields progress every 3 seconds."""
    if not DOCKER_AVAILABLE:
        error_json = json.dumps({
            "action": "error",
            "message": "Docker is not available",
        })
        yield f"{error_json}\n"
        return
    
    try:
        client = docker.from_env()
        
        # Build path is the volumn/runner directory
        build_path = os.path.join(settings.VOLUME_PATH, "runner")
        
        # Yield start message
        start_json = json.dumps({
            "action": "building github runner image",
            "status": "starting",
            "path": build_path,
        })
        yield f"{start_json}\n"
        
        last_yield_time = time.time()
        build_lines = []
        
        # Build the image with streaming
        for line in client.api.build(
            path=build_path,
            tag="gh_runner:latest",
            stream=True,
            decode=True,
        ):
            # Extract build output
            output = line.get("stream", "").strip()
            
            if output:
                build_lines.append(output)
                
                # Yield every 3 seconds or on important events
                current_time = time.time()
                should_yield = (
                    current_time - last_yield_time >= 3 or
                    "Successfully built" in output or
                    "Successfully tagged" in output or
                    "error" in output.lower()
                )
                
                if should_yield and build_lines:
                    # Combine accumulated lines
                    build_output = "\n".join(build_lines[-5:])  # Last 5 lines
                    progress_json = json.dumps({
                        "action": "building github runner image",
                        "status": "building",
                        "output": build_output,
                    })
                    yield f"{progress_json}\n"
                    last_yield_time = current_time
        
        # Yield completion message
        completion_json = json.dumps({
            "action": "building github runner image",
            "status": "completed",
            "message": "GitHub runner image built successfully",
            "image_tag": "gh_runner:latest",
        })
        yield f"{completion_json}\n"
        
    except Exception as e:
        error_json = json.dumps({
            "action": "error",
            "message": f"Failed to build runner image: {str(e)}",
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
    
    # Step 2: Download latest runner image (skip if available and digest matches)
    latest_release = _get_latest_release()
    if not latest_release or not latest_release.get("download_url"):
        error_json = json.dumps({
            "action": "error",
            "message": "Could not find latest runner release",
        })
        yield f"{error_json}\n"
        return
    
    # Get the expected digest from the release
    expected_digest = latest_release.get("digest")
    
    if _is_runner_binary_available_and_valid(expected_digest):
        skip_json = json.dumps({
            "action": "pulling latest action runner",
            "status": "skipped",
            "message": "Runner binary already available and digest verified, skipping download",
            "digest": expected_digest,
        })
        yield f"{skip_json}\n"
    else:
        runners_dir = os.path.join(settings.VOLUME_PATH, "runner")
        filename = "actions-runner-linux-x64.tar.gz"
        filepath = os.path.join(runners_dir, filename)
        
        yield from _download_with_progress_streaming(latest_release["download_url"], filepath)
    
    # Step 3: Pull ubuntu Docker image (skip if already available)
    if _is_ubuntu_image_available():
        skip_json = json.dumps({
            "action": "pulling ubuntu docker image",
            "status": "skipped",
            "message": "Ubuntu image already available, skipping pull",
        })
        yield f"{skip_json}\n"
    else:
        yield from _pull_ubuntu_docker_image()
    
    # Step 4: Build GitHub runner Docker image
    yield from _build_docker_image()
    
    # Step 5: Mark setup as complete
    from inc.utils.meta import set_meta
    set_meta("is_setup", True, meta_type="bool")
    
    final_json = json.dumps({
        "action": "setup",
        "status": "completed",
        "message": "System setup completed successfully",
    })
    yield f"{final_json}\n"
