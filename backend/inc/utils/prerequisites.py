import platform
import psutil
import distro
import os
from typing import Dict, Any, List
from pydantic import BaseModel
from inc.config import settings

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class PrerequisiteCheck(BaseModel):
    key: str
    status: bool
    message: str
    mandatory: bool


class PrerequisitesResponse(BaseModel):
    checks: List[PrerequisiteCheck]
    status: bool


def get_cpu_architecture() -> str:
    """Get CPU architecture (e.g., 'x86_64', 'ARM64')"""
    return platform.machine()


def get_total_ram_gb() -> float:
    """Get total RAM in GB"""
    return psutil.virtual_memory().total / (1024 ** 3)


def is_debian_based() -> bool:
    """Check if system is Debian or Ubuntu based"""
    os_id = distro.id()
    return os_id in ["debian", "ubuntu"]


def is_docker_available() -> bool:
    """Check if Docker daemon is running and accessible"""
    if not DOCKER_AVAILABLE:
        return False
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


def is_gh_runner_image_available() -> bool:
    """Check if 0xaungkon/gh-runner:latest Docker image is available"""
    if not is_docker_available():
        return False
    try:
        client = docker.from_env()
        images = client.images.list()
        for image in images:
            # Check if any tag matches 0xaungkon/gh-runner:latest
            if image.tags:
                for tag in image.tags:
                    if tag == "0xaungkon/gh-runner:latest":
                        return True
        return False
    except Exception:
        return False


def check_prerequisites() -> PrerequisitesResponse:
    """
    Check all system prerequisites.
    Returns a response with individual checks and a global status.
    All checks are mandatory for system setup.
    """
    checks: List[PrerequisiteCheck] = []

    # Check 1: Docker Available
    docker_available = is_docker_available()
    checks.append(
        PrerequisiteCheck(
            key="docker_available",
            status=docker_available,
            message="Docker daemon is running and accessible"
            if docker_available
            else "Docker daemon is not running or not accessible",
            mandatory=True,
        )
    )

    # Check 2: Debian/Ubuntu Based OS
    debian_based = is_debian_based()
    checks.append(
        PrerequisiteCheck(
            key="debian_ubuntu_os",
            status=debian_based,
            message=f"System is {distro.name(pretty=True)}"
            if debian_based
            else f"System is {distro.name(pretty=True)}, only Debian/Ubuntu are supported",
            mandatory=True,
        )
    )

    # Check 3: 64-bit CPU Architecture
    cpu_arch = get_cpu_architecture()
    is_64bit = "64" in cpu_arch or cpu_arch in ["x86_64", "amd64", "arm64", "aarch64"]
    checks.append(
        PrerequisiteCheck(
            key="cpu_64bit",
            status=is_64bit,
            message=f"CPU architecture is {cpu_arch} (64-bit)"
            if is_64bit
            else f"CPU architecture is {cpu_arch}, 64-bit required",
            mandatory=True,
        )
    )

    # Check 4: Minimum RAM 1GB
    ram_gb = get_total_ram_gb()
    sufficient_ram = ram_gb >= 1.0
    checks.append(
        PrerequisiteCheck(
            key="minimum_ram",
            status=sufficient_ram,
            message=f"System has {ram_gb:.2f} GB RAM available"
            if sufficient_ram
            else f"System has {ram_gb:.2f} GB RAM, minimum 1 GB required",
            mandatory=True,
        )
    )

    # Check 5: GitHub Runner Docker Image Available
    gh_runner_image_available = is_gh_runner_image_available()
    checks.append(
        PrerequisiteCheck(
            key="gh_runner_docker_image",
            status=gh_runner_image_available,
            message="0xaungkon/gh-runner:latest Docker image is available"
            if gh_runner_image_available
            else "0xaungkon/gh-runner:latest Docker image is not available",
            mandatory=False,
        )
    )

    # Global status is True only if all MANDATORY checks pass
    # gh_runner_docker_image does not affect global status
    global_status = all(check.status for check in checks if check.mandatory)

    return PrerequisitesResponse(checks=checks, status=global_status)
