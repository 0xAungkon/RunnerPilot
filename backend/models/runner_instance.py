from peewee import CharField, TextField, DateTimeField
from datetime import datetime
from inc.helpers.model import BaseModel


class RunnerInstance(BaseModel):
    github_url = CharField()
    token = TextField()
    hostname = CharField(null=True)
    label = CharField(null=True)
    command = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
