import sqlite3
from pathlib import Path
from urllib.parse import unquote, urlparse


SCHEMA = """
CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    weather_condition TEXT NOT NULL,
    recorded_at TEXT NOT NULL
)
"""

MYSQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    city_name VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    temperature DECIMAL(10, 2) NOT NULL,
    humidity DECIMAL(5, 2) NOT NULL,
    weather_condition VARCHAR(255) NOT NULL,
    recorded_at VARCHAR(40) NOT NULL
)
"""

MYSQL_URL_PREFIXES = ("mysql://", "mysql+pymysql://")


def get_connection(database_path: str | Path) -> sqlite3.Connection:
    if isinstance(database_path, str) and database_path.startswith(MYSQL_URL_PREFIXES):
        return _get_mysql_connection(database_path)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: str | Path) -> None:
    if isinstance(database_path, str) and database_path.startswith(MYSQL_URL_PREFIXES):
        _ensure_mysql_database(database_path)
        with get_connection(database_path) as connection:
            connection.execute(MYSQL_SCHEMA)
            connection.commit()
        return

    path = Path(database_path)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(path) as connection:
        connection.execute(SCHEMA)
        connection.commit()


class MySQLConnection:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, parameters=()):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query.replace("?", "%s"), parameters)
        return cursor

    def commit(self):
        self.connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.connection.close()


def _get_mysql_connection(database_url: str) -> MySQLConnection:
    try:
        import mysql.connector
    except ImportError as error:
        raise RuntimeError(
            "MySQL support requires mysql-connector-python. Install requirements.txt."
        ) from error

    parsed = urlparse(database_url)
    if not parsed.hostname or not parsed.path.strip("/"):
        raise ValueError("CITY_API_DATABASE_URL must include a MySQL host and database name.")
    connection = mysql.connector.connect(**_mysql_connection_options(parsed, include_database=True))
    return MySQLConnection(connection)


def _mysql_connection_options(parsed, include_database=False):
    options = {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
    }
    if include_database:
        options["database"] = parsed.path.strip("/")
    return options


def _ensure_mysql_database(database_url: str) -> None:
    import mysql.connector

    parsed = urlparse(database_url)
    database_name = parsed.path.strip("/")
    if not database_name:
        raise ValueError("CITY_API_DATABASE_URL must include a database name.")
    connection = mysql.connector.connect(**_mysql_connection_options(parsed))
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}`")
        connection.commit()
    finally:
        connection.close()
