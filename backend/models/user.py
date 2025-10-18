from peewee import Model, CharField
from inc.helpers.model import BaseModel

class User(BaseModel):
    name = CharField(unique=True)
    email = CharField(unique=True)
