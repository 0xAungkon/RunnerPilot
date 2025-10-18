from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from inc.utils.prerequisites import check_prerequisites, PrerequisitesResponse
from inc.utils.setup_helpers import setup_streaming_generator

router = APIRouter()


@router.get("/prerequisites", response_model=PrerequisitesResponse)
def get_prerequisites():
    """
    Check system prerequisites for RunnerPilot.
    
    Returns:
    - checks: List of individual prerequisite checks with status, message, and mandatory flag
    - status: True if all mandatory checks pass, False otherwise
    """
    return check_prerequisites()


@router.post("/setup")
def setup_system():
    """
    Setup the system by:
    1. Validating all prerequisites
    2. Downloading the latest runner image
    3. Pulling the ubuntu:latest Docker image
    
    Returns streaming JSON lines with progress updates.
    """
    return StreamingResponse(
        setup_streaming_generator(),
        media_type="application/x-ndjson"
    )
