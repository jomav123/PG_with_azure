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

2. Start PostgreSQL, then install dependencies and initialize the gallery table:

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

Database connection settings are loaded from the ignored `.env` file.
PostgreSQL uses port `5432`; Flask serves the web app on port `5000`. Uploaded
photos are stored in `instance/uploads/`. Supported image types are JPG, PNG,
GIF, and WEBP, up to 16 MB each.
