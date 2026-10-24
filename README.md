# Photo Gallery

A small Flask web app for creating and managing a personal photo gallery.
It supports adding, browsing, editing, replacing, and deleting photos.

## Run locally

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
PostgreSQL uses port `5432`; Flask serves the web app on port `5000`. Uploaded
photos are stored in `instance/uploads/`. Supported image types are JPG, PNG,
GIF, and WEBP, up to 16 MB each.

## Run tests

Tests also use PostgreSQL. Start the separate test database:

```powershell
docker compose up -d test-db
```

Set `TEST_DATABASE_URL` in `.env` to the `postgresql+psycopg2` URL for that
database, using port `5433` and a database name ending in `_test`. The test
fixture refuses any other database name because it drops and recreates the
gallery tables. Then run:

```powershell
python -m pytest
```
