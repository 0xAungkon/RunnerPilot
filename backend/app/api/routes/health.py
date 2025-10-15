import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependency import SessionDep
from sqlmodel import Session, text
from app.core.config import settings
from app.core.logging import logger
router = APIRouter(prefix="/health", tags=["health"])


def check_database(session: Session) -> Dict[str, Any]:
    """Check database connectivity and performance"""
    try:
        start_time = datetime.now(timezone.utc)
        
        # Simple query to test connection
        result = session.exec(text("SELECT 1 as test"))
        result.fetchone()
        
        end_time = datetime.now(timezone.utc)
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "timestamp": end_time.isoformat(),
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def check_external_services() -> Dict[str, Any]:
    """Check external service dependencies"""
    services = {}
    
    # Add checks for external services here
    # Example: Email service, SMS service, etc.
    
    return {
        "status": "healthy" if all(
            service.get("status") == "healthy" 
            for service in services.values()
        ) else "degraded",
        "services": services,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def get_system_info() -> Dict[str, Any]:
    """Get basic system information"""
    import platform
    
    try:
        # Try to import psutil with better error handling
        try:
            import psutil
        except ImportError as import_error:
            logger.error(f"psutil module not found: {import_error}")
            return {
                "error": "psutil module not installed",
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "message": "Install psutil package to get system metrics"
            }
        
        return {
            "hostname": platform.node(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "cpu_usage_percent": psutil.cpu_percent(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "memory_usage_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {"error": str(e)}


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service_name": settings.PROJECT_NAME,
        "stack_name": settings.SERVICE_NAME,
        "version": "1.0.0",
    }


@router.get("/ready")
def readiness_check(session: SessionDep):
    """Readiness check - checks if service is ready to handle requests"""
    checks = {}
    overall_status = "healthy"
    
    # Check database
    try:
        db_check = check_database(session)
        checks["database"] = db_check
        if db_check["status"] != "healthy":
            overall_status = "unhealthy"
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}
        overall_status = "unhealthy"
    
    response = {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }
    
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=response)
    
    return response


@router.get("/live")
def liveness_check():
    """Liveness check - checks if service is alive"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": "N/A",  # Could implement uptime tracking
    }


@router.get("/detailed")
def detailed_health_check(session: SessionDep):
    """Detailed health check with comprehensive system information"""
    start_time = datetime.now(timezone.utc)
    
    checks = {}
    try:
        checks["database"] = check_database(session)
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}

    try:
        checks["external_services"] = check_external_services()
    except Exception as e:
        checks["external_services"] = {"status": "error", "error": str(e)}

    # Determine overall status
    overall_status = "healthy"
    if checks["database"].get("status") != "healthy":
        overall_status = "unhealthy"
    elif checks["external_services"].get("status") not in ["healthy", "degraded"]:
        overall_status = "degraded"
    
    end_time = datetime.now(timezone.utc)
    total_check_time = (end_time - start_time).total_seconds() * 1000
    
    response = {
        "status": overall_status,
        "timestamp": end_time.isoformat(),
        "total_check_time_ms": round(total_check_time, 2),
        "service": {
            "name": settings.PROJECT_NAME,
            "stack_name": settings.SERVICE_NAME,
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
        },
        "checks": checks,
        "system": get_system_info(),
    }
    
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=response)
    
    return response


@router.get("/metrics")
def health_metrics():
    """Health metrics endpoint for monitoring systems"""
    try:
        system_info = get_system_info()
        
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_name": settings.PROJECT_NAME,
            "stack_name": settings.SERVICE_NAME,
            "environment": settings.ENVIRONMENT,
            "metrics": {
                "cpu_usage_percent": system_info.get("cpu_usage_percent", 0),
                "memory_usage_percent": system_info.get("memory_usage_percent", 0),
                "disk_usage_percent": system_info.get("disk_usage_percent", 0),
                "cpu_count": system_info.get("cpu_count", 0),
                "memory_total_gb": system_info.get("memory_total_gb", 0),
                "memory_available_gb": system_info.get("memory_available_gb", 0),
            }
        }
        
        return metrics
    except Exception as e:
        logger.error(f"Failed to get health metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")
