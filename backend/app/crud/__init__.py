import pkgutil
import importlib
import inspect

for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            globals()[name] = obj
