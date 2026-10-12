# City Information REST API

A Flask REST API for storing city-level weather information with SQLite or MySQL persistence.

## Setup

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

The default database is SQLite. To use MySQL, copy `.env.example` to `.env` and update
`CITY_API_DATABASE_URL` with your MySQL username, password, host, port, and database name.
The `.env` file is ignored by Git so credentials are not committed.

## MySQL setup

Start MySQL, then create the database and table using the included SQL script or the
Python initializer. The application and Python initializer create `city_weather`
automatically if it does not exist.

From the MySQL client:

```sql
SOURCE C:/Users/abhir/OneDrive/Desktop/DEProject/sql/mysql_schema.sql;
```

If the MySQL command-line client is installed and available on `PATH`, run this in PowerShell:

```powershell
Get-Content sql\mysql_schema.sql | mysql -u root -p
```

If PowerShell says `mysql is not recognized`, initialize the table through the Python
application instead:

```powershell
python scripts\initialize_mysql.py
```

This command uses `CITY_API_DATABASE_URL` from `.env`, so it does not require `mysql.exe`.

Then configure `.env`, for example:

```text
CITY_API_DATABASE_URL=mysql://root:your_password@127.0.0.1:3306/city_weather
```

The API creates the `cities` table automatically when it connects, but running the SQL
script first is useful for explicit database setup and verification.

## Run

```bash
python -m city_api.app
```

The API is available at `http://127.0.0.1:5000`.

Set `CITY_API_DATABASE` to use a different SQLite file. The default is `city_api/cities.db`.
`CITY_API_DATABASE_URL` takes precedence when both variables are set.

## Endpoints

- `GET /cities` lists all cities. Use `?state=Telangana` or `?min_temperature=30` to filter.
- `GET /cities/<id>` gets one city.
- `POST /cities` creates a city using the fields in the assessment example.
- `PUT /cities/<id>` updates one or more city fields.
- `DELETE /cities/<id>` removes a city.
- `GET /statistics` returns count, average, maximum, and minimum temperature.

## Tests

```bash
pytest
```
