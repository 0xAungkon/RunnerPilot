from peewee import SqliteDatabase
from .config import settings
from typing import List, Optional
import inspect

try:
	# local import to avoid importing models at module import time in some contexts
	import models as models_pkg
except Exception:
	models_pkg = None

db_path = settings.DATABASE_URL.replace("sqlite:///", "")
db = SqliteDatabase(db_path)


def init_db(models: list = None) -> None:
	"""Initialize the database connection and create tables.

	Args:
		models: Optional list of Peewee Model classes to create tables for.
	"""
	# Ensure database is connected before creating tables
	if db.is_closed():
		db.connect(reuse_if_open=True)

	if not models:
		# attempt to auto-discover models from the `models` package
		discovered: List = []
		if models_pkg is None:
			try:
				import importlib

				models_pkg = importlib.import_module("models")
			except Exception:
				models_pkg = None

		if models_pkg is not None:
			for name, obj in vars(models_pkg).items():
				# pick classes that are subclasses of peewee.Model
				try:
					if inspect.isclass(obj):
						# avoid importing peewee at module scope again
						from peewee import Model as PeeweeModel

						if issubclass(obj, PeeweeModel):
							discovered.append(obj)
				except Exception:
					# ignore non-class objects or issubclass errors
					continue

		models = discovered

	if models:
		db.create_tables(models)
