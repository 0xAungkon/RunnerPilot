

from fastapi import APIRouter
import importlib
import pkgutil
from app.core.logging import logger

from . import routes


exclude_routers = []  # Example: Add module names to exclude, e.g., ["files"]

api_router = APIRouter()

loaded_routers = []
for loader, module_name, is_pkg in pkgutil.iter_modules(routes.__path__):
    if module_name in exclude_routers:
        continue
    module = importlib.import_module(f".routes.{module_name}", package=__package__)
    if hasattr(module, "router"):
        api_router.include_router(module.router, prefix=f"", tags=[module_name])
        loaded_routers.append(module_name)

logger.info(f"Loaded routers: [ /{', /'.join(loaded_routers)}' ]")
