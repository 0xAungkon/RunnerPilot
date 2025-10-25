from peewee import Model, CharField
from inc.db import db

class BaseModel(Model):
    class Meta:
        database = db