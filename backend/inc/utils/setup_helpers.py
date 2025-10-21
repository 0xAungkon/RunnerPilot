import json
import os
import urllib.request
import time
from typing import Any, Generator
from inc.config import settings
from inc.utils.prerequisites import check_prerequisites

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


def _is_gh_runner_image_available() -> bool:
    """Check if 0xaungkon/gh-runner:latest Docker image is available."""
    if not DOCKER_AVAILABLE:
        return False
    try:
        client = docker.from_env()
        images = client.images.list()
        for image in images:
            if image.tags:
                for tag in image.tags:
                    if tag == "0xaungkon/gh-runner:latest":
                        return True
        return False
    except Exception:
        return False











def _pull_gh_runner_docker_image() -> Generator[str, None, None]:
    """Generator that pulls 0xaungkon/gh-runner:latest Docker image and yields progress every 3 seconds."""
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
            "action": "pulling gh-runner docker image",
            "status": "starting",
        })
        yield f"{start_json}\n"
        
        last_yield_time = time.time()
        
        # Pull the image with streaming
        for line in client.api.pull("0xaungkon/gh-runner:latest", stream=True, decode=True):
            # Extract relevant info from docker API response
            if "status" in line:
                status = line.get("status", "")
                progress = line.get("progress", "")
                
                # Yield progress every 3 seconds or when pull is complete
                current_time = time.time()
                if current_time - last_yield_time >= 3 or status in ["Pull complete", "Digest:", "Status:"]:
                    progress_json = json.dumps({
                        "action": "pulling gh-runner docker image",
                        "status": status,
                        "progress": progress,
                    })
                    yield f"{progress_json}\n"
                    last_yield_time = current_time
        
        # Yield completion message
        completion_json = json.dumps({
            "action": "pulling gh-runner docker image",
            "status": "completed",
            "message": "0xaungkon/gh-runner:latest image pulled successfully",
        })
        yield f"{completion_json}\n"
        
    except Exception as e:
        error_json = json.dumps({
            "action": "error",
            "message": f"Failed to pull gh-runner image: {str(e)}",
        })
        yield f"{error_json}\n"


def setup_streaming_generator() -> Generator[str, None, None]:
    """Main setup generator that validates and pulls the gh-runner image."""
    
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
    
    # Step 2: Pull gh-runner Docker image (skip if already available)
    if _is_gh_runner_image_available():
        skip_json = json.dumps({
            "action": "pulling gh-runner docker image",
            "status": "skipped",
            "message": "0xaungkon/gh-runner:latest already available, skipping pull",
        })
        yield f"{skip_json}\n"
    else:
        yield from _pull_gh_runner_docker_image()
    
    # Step 3: Mark setup as complete
    from inc.utils.meta import set_meta
    set_meta("is_setup", True, meta_type="bool")
    
    final_json = json.dumps({
        "action": "setup",
        "status": "completed",
        "message": "System setup completed successfully",
    })
    yield f"{final_json}\n"
