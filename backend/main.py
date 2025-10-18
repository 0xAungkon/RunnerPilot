from fastapi import FastAPI
from routers import meta
from inc.config import is_dev

app = FastAPI()


@app.on_event("startup")
async def startup_event():
	# Initialize DB connection and create tables for all models in `models` package
	from inc.db import init_db

	init_db()


from routers import auth, common
from routers import runners_release


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(common.router, prefix="/common", tags=["common"])

# Only include meta router in development environment
if is_dev():
	app.include_router(meta.router, prefix="/meta", tags=["meta"])

app.include_router(runners_release.router, tags=["runners"], include_in_schema=True)
