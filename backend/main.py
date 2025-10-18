from fastapi import FastAPI
from inc.db import db
from models import User
from routers import users

app = FastAPI()

db.connect()
db.create_tables([User])

app.include_router(users.router, prefix="/users", tags=["users"])
