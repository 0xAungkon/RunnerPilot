from peewee import AutoField, CharField, TextField
from inc.helpers.model import BaseModel

class Meta(BaseModel):
    id = AutoField(primary_key=True)
    meta_key = CharField(unique=True)
    meta_value = TextField(null=True)
    meta_type = CharField()
