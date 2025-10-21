from peewee import CharField, TextField, DateTimeField
from datetime import datetime
import string
import random
from inc.helpers.model import BaseModel


def generate_unique_suffix():
    """Generate a random 6-character suffix for runner name (alphanumeric only, no symbols)."""
    # Use only letters and digits (no symbols)
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6)).lower()


class RunnerInstance(BaseModel):
    runner_name = CharField(unique=True)
    github_url = CharField()
    token = TextField()
    labels = TextField(null=True)  # Comma-separated labels or JSON
    hostname = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    
    @staticmethod
    def generate_runner_name(base_name: str) -> str:
        """Generate a unique runner name with base_name-XXXXXX format."""
        suffix = generate_unique_suffix()
        return f"{base_name}-{suffix}"
