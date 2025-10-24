from fastapi import FastAPI
from routers import meta
from inc.config import is_dev
import json, random

app = FastAPI()


@app.on_event("startup")
async def startup_event():
	# Initialize DB connection and create tables for all models in `models` package
	from inc.db import init_db

	init_db()


from routers import auth, common
from routers import runner_instance
from routers import system
import random

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(common.router, prefix="/common", tags=["common"])
app.include_router(system.router, prefix="/system", tags=["system"])


with open("jokes.json", "r") as f:
	_jokes = json.load(f)

@app.get("/", tags=["root"])
async def root():
	return {"joke": random.choice(_jokes)}

if is_dev():
	app.include_router(meta.router, prefix="/meta", tags=["meta"])

app.include_router(runner_instance.router, tags=["runners"], include_in_schema=True)
