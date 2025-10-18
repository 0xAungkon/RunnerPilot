from fastapi import APIRouter
from inc.utils.prerequisites import check_prerequisites, PrerequisitesResponse
from inc.utils.meta import set_meta, get_meta

router = APIRouter()


@router.get("/prerequisites", response_model=PrerequisitesResponse)
def get_prerequisites():
    """
    Check system prerequisites for RunnerPilot.
    
    Returns:
    - checks: List of individual prerequisite checks with status, message, and mandatory flag
    - global_status: True if all mandatory checks pass, False otherwise
    """
    return check_prerequisites()


@router.post("/setup")
def setup_system():
    """
    Mark the system as setup by updating the is_setup meta flag.
    
    Only call this after verifying that all prerequisites are met.
    """
    set_meta("is_setup", True, meta_type="bool")
    return {
        "status": "success",
        "message": "System setup completed",
        "is_setup": get_meta("is_setup")
    }
