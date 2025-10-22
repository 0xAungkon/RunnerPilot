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

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

router = APIRouter()

RUNNERS_DIR = os.path.join(settings.VOLUME_PATH, "runner")


# -------- Models ---------

class RunnerInstanceOut(BaseModel):
    id: int
    runner_name: str
    github_url: str
    token: str
    labels: Optional[str]
    hostname: Optional[str]
    created_at: str
    status: str  # "active", "inactive", "error"

    class Config:
        from_attributes = True


class CreateRunnerInstanceIn(BaseModel):
    runner_name: Optional[str] = None  # Optional, will auto-generate if not provided
    github_url: str
    token: str
    labels: Optional[str] = None


class UpdateRunnerInstanceIn(BaseModel):
    token: str


class CloneRunnerInstanceIn(BaseModel):
    token: Optional[str] = None
    count: int = 1


class DeleteRunnerInstanceIn(BaseModel):
    id: int


# -------- Helpers ---------

def _get_instance_status(instance: RunnerInstance) -> str:
    """Determine the status of a runner instance by checking docker container state."""
    if not DOCKER_AVAILABLE or not instance.hostname:
        return "inactive"
    
    try:
        client = docker.from_env()
        container = client.containers.get(instance.runner_name)
        
        if container.status == "running":
            return "active"
        elif container.status == "exited":
            return "inactive"
        else:
            return "error"
    except docker.errors.NotFound:
        return "inactive"
    except Exception:
        return "error"


def _run_docker_container(
    runner_name: str,
    github_url: str,
    token: str,
    labels: Optional[str] = None,
) -> tuple[bool, str, Optional[str]]:
    """
    Run a Docker container for the GitHub runner.
    
    Returns:
        tuple: (success: bool, message: str, container_id: Optional[str])
    """
    if not DOCKER_AVAILABLE:
        return False, "Docker is not available", None
    
    try:
        client = docker.from_env()
        
        # Prepare environment variables
        env = {
            "RUNNER_URL": github_url,
            "RUNNER_TOKEN": token,
            "RUNNER_NAME": runner_name,
        }
        
        if labels:
            env["RUNNER_LABELS"] = labels
        
        # Prepare volumes - mount docker socket for running docker commands inside the runner
        volumes = {
            "/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}
        }
        
        # Run the container
        container = client.containers.run(
            image="0xaungkon/gh-runner:latest",
            environment=env,
            volumes=volumes,
            detach=True,  # Run in background
            restart_policy={"Name": "unless-stopped"},
            name=runner_name,  # Use runner_name as container name
        )
        
        return True, f"Container started successfully", container.id
        
    except docker.errors.ImageNotFound:
        return False, "Docker image 0xaungkon/gh-runner:latest not found", None
    except docker.errors.ContainerError as e:
        return False, f"Container error: {str(e)}", None
    except Exception as e:
        return False, f"Failed to run container: {str(e)}", None


# -------- Routes ----------

@router.get("/runner", response_model=List[RunnerInstanceOut])
async def list_instances(user: AuthorizedUser = Depends(authorized_user)):
    """List all runner instances."""
    try:
        instances = RunnerInstance.select()
        result = []
        for instance in instances:
            result.append(
                RunnerInstanceOut(
                    id=instance.id,
                    runner_name=instance.runner_name,
                    github_url=instance.github_url,
                    token=instance.token,
                    labels=instance.labels,
                    hostname=instance.hostname,
                    created_at=instance.created_at.isoformat(),
                    status=_get_instance_status(instance),
                )
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list instances: {str(e)}")


@router.post("/runner", response_model=RunnerInstanceOut)
async def create_instance(
    payload: CreateRunnerInstanceIn,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Create a new runner instance."""
    try:
        # Generate runner name if not provided
        runner_name = payload.runner_name
        if not runner_name:
            # Generate a default name with timestamp or counter
            runner_name = f"runner"
        
        runner_name = RunnerInstance.generate_runner_name(runner_name)
        
        # Create the database record first
        instance = RunnerInstance.create(
            runner_name=runner_name,
            github_url=payload.github_url,
            token=payload.token,
            labels=payload.labels,
        )
        
        # Try to run the docker container
        success, message, container_id = _run_docker_container(
            runner_name=runner_name,
            github_url=payload.github_url,
            token=payload.token,
            labels=payload.labels,
        )
        
        if success:
            # Update hostname with container ID
            instance.hostname = container_id
            instance.save()
        else:
            # Log the error but still return the instance record
            print(f"Warning: Docker container creation failed: {message}")
        
        return RunnerInstanceOut(
            id=instance.id,
            runner_name=instance.runner_name,
            github_url=instance.github_url,
            token=instance.token,
            labels=instance.labels,
            hostname=instance.hostname,
            created_at=instance.created_at.isoformat(),
            status=_get_instance_status(instance),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create instance: {str(e)}")


@router.delete("/runner/{instance_id}")
async def delete_instance(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Delete a runner instance and its container."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        
        # Stop and remove the docker container if it exists
        if DOCKER_AVAILABLE and instance.runner_name:
            try:
                client = docker.from_env()
                try:
                    container = client.containers.get(instance.runner_name)
                    container.stop()
                    container.remove()
                except docker.errors.NotFound:
                    pass  # Container already removed
            except Exception as e:
                print(f"Warning: Failed to remove container: {str(e)}")
        
        # Delete the database record
        instance.delete_instance()
        return {"status": "ok", "message": f"Instance {instance_id} deleted (container removed)", "id": instance_id}
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete instance: {str(e)}")


@router.put("/runner/{instance_id}")
async def update_instance(
    instance_id: int,
    payload: UpdateRunnerInstanceIn,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Update a runner instance (token only)."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        instance.token = payload.token
        instance.save()
        return RunnerInstanceOut(
            id=instance.id,
            runner_name=instance.runner_name,
            github_url=instance.github_url,
            token=instance.token,
            labels=instance.labels,
            hostname=instance.hostname,
            created_at=instance.created_at.isoformat(),
            status=_get_instance_status(instance),
        )
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update instance: {str(e)}")


@router.post("/runner/{instance_id}/clone")
async def clone_instance(
    instance_id: int,
    payload: CloneRunnerInstanceIn,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Clone/setup multiple runner instances based on count."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        
        # Use provided token or fall back to instance token
        token = payload.token or instance.token
        count = payload.count
        
        if count < 1:
            raise HTTPException(status_code=400, detail="Count must be at least 1")
        
        created_instances = []
        failed_clones = []
        
        # Create multiple instances
        for i in range(count):
            try:
                # Generate unique runner name for each clone
                clone_base_name = f"{instance.runner_name}-clone"
                clone_runner_name = RunnerInstance.generate_runner_name(clone_base_name)
                
                # Create database record
                cloned_instance = RunnerInstance.create(
                    runner_name=clone_runner_name,
                    github_url=instance.github_url,
                    token=token,
                    labels=instance.labels,
                )
                
                # Try to run the docker container
                success, message, container_id = _run_docker_container(
                    runner_name=clone_runner_name,
                    github_url=instance.github_url,
                    token=token,
                    labels=instance.labels,
                )
                
                if success:
                    cloned_instance.hostname = container_id
                    cloned_instance.save()
                    created_instances.append({
                        "id": cloned_instance.id,
                        "runner_name": clone_runner_name,
                        "status": "running",
                        "container_id": container_id,
                    })
                else:
                    failed_clones.append({
                        "runner_name": clone_runner_name,
                        "error": message,
                    })
                    
            except Exception as e:
                failed_clones.append({
                    "error": f"Clone {i+1} failed: {str(e)}",
                })
        
        return {
            "status": "completed",
            "message": f"Clone process completed: {len(created_instances)} successful, {len(failed_clones)} failed",
            "instance_id": instance_id,
            "count": count,
            "created_instances": created_instances,
            "failed_clones": failed_clones if failed_clones else None,
        }
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone instance: {str(e)}")


def _stream_container_logs(instance_id: int) -> Any:
    """Generator that streams container logs in real-time."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        
        if not DOCKER_AVAILABLE or not instance.hostname:
            error_json = json.dumps({
                "status": "error",
                "message": "Container not available",
            })
            yield f"{error_json}\n"
            return
        
        try:
            client = docker.from_env()
            container = client.containers.get(instance.runner_name)
            
            # Get initial logs
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            if logs:
                for line in logs.split('\n'):
                    if line.strip():
                        log_json = json.dumps({
                            "status": "streaming",
                            "log": line,
                        })
                        yield f"{log_json}\n"
            
            # Stream new logs in real-time
            for log_line in container.logs(stream=True, stdout=True, stderr=True):
                decoded_line = log_line.decode('utf-8').strip()
                if decoded_line:
                    log_json = json.dumps({
                        "status": "streaming",
                        "log": decoded_line,
                    })
                    yield f"{log_json}\n"
                    
        except docker.errors.NotFound:
            error_json = json.dumps({
                "status": "error",
                "message": "Container not found",
            })
            yield f"{error_json}\n"
    except RunnerInstance.DoesNotExist:
        error_json = json.dumps({
            "status": "error",
            "message": f"Instance {instance_id} not found",
        })
        yield f"{error_json}\n"
    except Exception as e:
        error_json = json.dumps({
            "status": "error",
            "message": f"Failed to stream logs: {str(e)}",
        })
        yield f"{error_json}\n"



@router.get("/runner/{instance_id}/logs")
async def get_instance_logs(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Stream logs for a runner instance from the docker container in real-time."""
    return StreamingResponse(
        _stream_container_logs(instance_id),
        media_type="application/x-ndjson"
    )


@router.post("/runner/{instance_id}/start")
async def start_instance(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Start a runner instance."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        
        # Try to run the docker container
        success, message, container_id = _run_docker_container(
            runner_name=instance.runner_name,
            github_url=instance.github_url,
            token=instance.token,
            labels=instance.labels,
        )
        
        if success:
            # Update hostname with container ID
            instance.hostname = container_id
            instance.save()
            return {
                "status": "started",
                "message": message,
                "instance_id": instance_id,
                "container_id": container_id,
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to start container: {message}")
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start instance: {str(e)}")


@router.post("/runner/{instance_id}/stop")
async def stop_instance(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Stop a runner instance (container remains for restart)."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        
        if not DOCKER_AVAILABLE:
            raise HTTPException(status_code=500, detail="Docker is not available")
        
        try:
            client = docker.from_env()
            
            # Try to stop the container by name
            try:
                container = client.containers.get(instance.runner_name)
                container.stop()
                return {
                    "status": "stopped",
                    "message": "Container stopped (can be restarted)",
                    "instance_id": instance_id,
                    "container_id": container.id,
                }
            except docker.errors.NotFound:
                return {
                    "status": "not_running",
                    "message": "Container not found (already stopped?)",
                    "instance_id": instance_id,
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Docker error: {str(e)}")
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop instance: {str(e)}")


@router.post("/runner/{instance_id}/restart")
async def restart_instance(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Restart a runner instance (stop and start)."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        
        if not DOCKER_AVAILABLE:
            raise HTTPException(status_code=500, detail="Docker is not available")
        
        try:
            client = docker.from_env()
            
            try:
                container = client.containers.get(instance.runner_name)
                
                # Stop the container
                container.stop()
                
                # Start the container again
                container.start()
                
                return {
                    "status": "restarted",
                    "message": "Container restarted successfully",
                    "instance_id": instance_id,
                    "container_id": container.id,
                    "container_status": "running",
                }
            except docker.errors.NotFound:
                raise HTTPException(status_code=404, detail=f"Container not found for instance {instance_id}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Docker error: {str(e)}")
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart instance: {str(e)}")


@router.post("/runner/{instance_id}/logs/clear")
async def clear_instance_logs(
    instance_id: int,
    user: AuthorizedUser = Depends(authorized_user),
):
    """Clear/truncate logs for a runner instance container."""
    try:
        instance = RunnerInstance.get_by_id(instance_id)
        
        if not DOCKER_AVAILABLE:
            raise HTTPException(status_code=500, detail="Docker is not available")
        
        try:
            client = docker.from_env()
            container = client.containers.get(instance.runner_name)
            
            # Truncate container logs by using the truncate method on the container
            # Docker API doesn't have a native truncate, so we use a workaround:
            # We can't directly truncate, but we can document this limitation
            # In practice, users typically restart the container to clear logs
            
            # For now, we'll return a message about the workaround
            return {
                "status": "info",
                "message": "Docker logs cannot be truncated directly. Restart container to clear logs.",
                "instance_id": instance_id,
                "container_id": container.id,
            }
        except docker.errors.NotFound:
            raise HTTPException(status_code=404, detail=f"Container not found for instance {instance_id}")
    except RunnerInstance.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")
