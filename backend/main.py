from fastapi import FastAPI
from routers import users

app = FastAPI()


@app.on_event("startup")
async def startup_event():
	# Initialize DB connection and create tables for all models in `models` package
	from inc.db import init_db

	init_db()


app.include_router(users.router, prefix="/users", tags=["users"])
