import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

from city_api.database import initialize_database


load_dotenv()
database_url = os.environ.get("CITY_API_DATABASE_URL")
if not database_url or not database_url.startswith(("mysql://", "mysql+pymysql://")):
    raise SystemExit("Set CITY_API_DATABASE_URL to a MySQL URL in .env first.")

initialize_database(database_url)

print("MySQL cities table is ready.")