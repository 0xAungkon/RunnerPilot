from peewee import SqliteDatabase
from .config import settings

db_path = settings.DATABASE_URL.replace("sqlite:///", "")
db = SqliteDatabase(db_path)
