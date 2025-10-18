from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from inc.auth import AuthorizedUser, authorized_user
from inc.config import settings
from models import RunnerInstance

router = APIRouter()

RUNNERS_DIR = os.path.join(settings.VOLUME_PATH, "runner")


# -------- Models ---------

class RunnerInstanceOut(BaseModel):
    id: int
    github_url: str
    token: str
    hostname: Optional[str]
    label: Optional[str]
    created_at: str
    status: str  # "active", "inactive", "error"

    class Config:
        from_attributes = True


class CreateRunnerInstanceIn(BaseModel):
    github_url: str
    token: str
    label: Optional[str] = None
    command: Optional[str] = None


class DeleteRunnerInstanceIn(BaseModel):
    id: int


# -------- Helpers ---------

def _get_instance_status(instance: RunnerInstance) -> str:
    """Determine the status of a runner instance."""
    # For now, return 'active' as default
    # In future, this can check if the instance is actually running
    return "active"


def _execute_command_stream(instance_id: int, cmd: str) -> Any:
    """Generator that yields command execution output as JSON lines."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        # TODO: Implement actual command execution logic
        # This would involve executing the command on the runner instance
        # and streaming the output back
        
        # Simulated command execution
        output_lines = [
            f"Executing command on instance {instance_id}: {cmd}",
            "Line 1 of output",
            "Line 2 of output",
            "Command completed successfully",
        ]
        
        for line in output_lines:
            output_json = json.dumps({
                "status": "running",
                "output": line,
            })
            yield f"{output_json}\n"
        
        # Yield completion
        completion_json = json.dumps({
            "status": "completed",
            "message": "Command execution completed",
        })
        yield f"{completion_json}\n"

    except RunnerInstance.DoesNotExist:
        error_json = json.dumps({
            "status": "error",
            "message": f"Instance {instance_id} not found",
        })
        yield f"{error_json}\n"
    except Exception as e:
        error_json = json.dumps({
            "status": "error",
            "message": str(e),
        })
        yield f"{error_json}\n"


# -------- Routes ----------

@router.get("/runners/instance", response_model=List[RunnerInstanceOut])
async def list_instances(user: AuthorizedUser = Depends(authorized_user)):
    """List all runner instances."""
    try:
        instances = RunnerInstance.select()
        result = []
        for instance in instances:
            result.append(
                RunnerInstanceOut(
                    id=instance.id,
                    github_url=instance.github_url,
                    token=instance.token,
                    hostname=instance.hostname,
                    label=instance.label,
                    created_at=instance.created_at.isoformat(),
                    status=_get_instance_status(instance),
                )
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list instances: {str(e)}")


@router.post("/runners/instance", response_model=RunnerInstanceOut)
async def create_instance(
    payload: CreateRunnerInstanceIn,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Create a new runner instance."""
    try:
        instance = RunnerInstance.create(
            github_url=payload.github_url,
            token=payload.token,
            label=payload.label,
            command=payload.command,
        )
        return RunnerInstanceOut(
            id=instance.id,
            github_url=instance.github_url,
            token=instance.token,
            hostname=instance.hostname,
            label=instance.label,
            created_at=instance.created_at.isoformat(),
            status=_get_instance_status(instance),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create instance: {str(e)}")


@router.delete("/runners/instance/{instance_id}")
async def delete_instance(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Delete a runner instance by ID."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        instance.delete_instance()
        return {"status": "ok", "message": f"Instance {instance_id} deleted", "id": instance_id}
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete instance: {str(e)}")


@router.post("/runners/instance/{instance_id}/clone")
async def clone_instance(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Clone/setup a runner instance."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        # TODO: Implement actual clone logic
        # This would involve cloning the runner repository and setting up the instance
        return {
            "status": "cloning",
            "message": "Clone process started",
            "instance_id": instance_id,
        }
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone instance: {str(e)}")


@router.get("/runners/instance/{instance_id}/logs")
async def get_instance_logs(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Get logs for a runner instance."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        # TODO: Implement actual log retrieval logic
        # This would involve reading logs from the instance directory
        return {
            "instance_id": instance_id,
            "logs": [],
            "message": "No logs available yet",
        }
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


@router.post("/runners/instance/{instance_id}/rebuild")
async def rebuild_instance(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Rebuild a runner instance."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        # TODO: Implement actual rebuild logic
        # This would involve stopping the current instance and rebuilding it
        return {
            "status": "rebuilding",
            "message": "Rebuild process started",
            "instance_id": instance_id,
        }
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rebuild instance: {str(e)}")


@router.post("/runners/instance/{instance_id}/start")
async def start_instance(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Start a runner instance."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        # TODO: Implement actual start logic
        # This would involve starting the runner process
        return {
            "status": "starting",
            "message": "Start process initiated",
            "instance_id": instance_id,
        }
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start instance: {str(e)}")


@router.post("/runners/instance/{instance_id}/stop")
async def stop_instance(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Stop a runner instance."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        # TODO: Implement actual stop logic
        # This would involve stopping the runner process
        return {
            "status": "stopping",
            "message": "Stop process initiated",
            "instance_id": instance_id,
        }
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop instance: {str(e)}")


class ExecuteCommandIn(BaseModel):
    command: str


@router.post("/runners/instance/{instance_id}/command")
async def execute_command(
    instance_id: int,
    payload: ExecuteCommandIn,
    user: AuthorizedUser = Depends(authorized_user),
):
    """
    Execute a command on a runner instance.
    Streams command output as JSON lines.
    """
    return StreamingResponse(
        _execute_command_stream(instance_id, payload.command),
        media_type="application/x-ndjson"
    )
