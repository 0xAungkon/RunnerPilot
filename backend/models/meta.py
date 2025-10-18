from peewee import CharField, TextField
from inc.helpers.model import BaseModel

class Meta(BaseModel):
    meta_key = CharField(primary_key=True)
    meta_value = TextField(null=True)
    meta_type = CharField()
