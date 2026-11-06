# Photo Gallery

A small Flask web app for creating and managing a personal photo gallery.
It supports adding, browsing, editing, replacing, and deleting photos.

## Run with Docker Desktop

Make sure Docker Desktop is running. From the project folder, start the web app
and PostgreSQL together:

```powershell
docker compose up --build -d
```

Open <http://127.0.0.1:5000>. In Docker Desktop, find the Compose project to see
the `app` and `db` containers, view their logs, or stop them. The first startup
builds the app image, waits for PostgreSQL to become healthy, and initializes
the gallery table.

Stop the containers without deleting saved database data or uploaded images:

```powershell
docker compose down
```

## Access the database once the cointainer is running

```powershell
docker compose exec db psql -U postgres -d photo_gallery
```

To see records: 
docker compose exec db psql -U postgres -d photo_gallery -c "SELECT id, title, filename FROM photo;"


To quit : \q



## Run locally without containerizing the app

1. Create and activate a virtual environment once per terminal session:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If the prompt already shows `(.venv)`, it is active; do not activate it again.

2. Start the Docker PostgreSQL database, install dependencies, and initialize
   the gallery table:

   ```powershell
   docker compose up -d db
   pip install -r requirements.txt
   flask --app app init-db
   ```

3. Start the app directly:

   ```powershell
   python app.py
   ```

4. Open <http://127.0.0.1:5000>.

The app reads its PostgreSQL connection URL from `DATABASE_URL` in the ignored
`.env` file and requires PostgreSQL; it has no other database backend.

The browser connects to the Flask web app on port `5000`. PostgreSQL listens on
port `5432` for database connections; the app container connects to it at
`db:5432` over Docker's private network. In a port mapping such as
`5000:5000`, the left port is on your computer and the right port is inside the
container. The app and database are different services, so they need different
host ports. If port `5000` is already in use, change the app mapping to
`5001:5000` and open <http://127.0.0.1:5001>. Uploaded photos are stored
persistently in Docker's `uploads` volume when containerized, or in
`instance/uploads/` when run locally. Supported image types are JPG, PNG, GIF,
and WEBP, up to 16 MB each.

## Run tests

Tests also use PostgreSQL. Start the separate test database:

```powershell
docker compose --profile test up -d test-db
```

Set `TEST_DATABASE_URL` in `.env` to the `postgresql+psycopg2` URL for that
database, using port `5433` and a database name ending in `_test`. The test
fixture refuses any other database name because it drops and recreates the
gallery tables. Then run:

```powershell
python -m pytest
```

## Pushing through github

git add .
git status
git commit -m "Publish photo gallery app"
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
note: Whether both local and remonte have the same folder's name it would lead to conflict

## azure database connections
export PGHOST=photogallery.postgres.database.azure.com
export PGUSER=jopostgre
export PGPORT=5432
export PGDATABASE=postgres
export PGPASSWORD="azertyUIOP1234" 