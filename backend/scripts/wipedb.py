import os
import glob
from psycopg import connect
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

if os.getenv("ENVIRONMENT") != "local":
    print("Error: Database wipe is only allowed in local environment.")
    exit(1)

confirm = input("Are you sure you want to delete the database? (y/n): ")
if confirm.lower() != "y":
    print("Aborted.")
    exit(0)

with connect(
    host=os.getenv("POSTGRES_SERVER"),
    port=os.getenv("POSTGRES_PORT"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    dbname=os.getenv("POSTGRES_DB"),
) as conn:
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    conn.commit()

versions_dir = os.path.join(os.path.dirname(__file__), "../alembic/versions")
for file_path in glob.glob(os.path.join(versions_dir, "*")):
    if os.path.isfile(file_path):
        os.remove(file_path)

print("Database wiped successfully.")
