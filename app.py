from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import String, Text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


load_dotenv()


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
MAX_UPLOAD_BYTES = 16 * 1024 * 1024


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()


class Photo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), unique=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    instance_path = Path(app.instance_path)
    app.config.from_mapping(
        SECRET_KEY="local-development-key",
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES,
        UPLOAD_FOLDER=str(instance_path / "uploads"),
    )
    if test_config:
        app.config.update(test_config)
    require_postgres_database(app)

    instance_path.mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)

    @app.get("/")
    def index():
        photos = db.session.scalars(
            db.select(Photo).order_by(Photo.created_at.desc(), Photo.id.desc())
        ).all()
        return render_template("index.html", photos=photos)

    @app.route("/photos/new", methods=["GET", "POST"])
    def create_photo():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            image = request.files.get("image")

            if not title:
                flash("Enter a title for the photo.", "error")
            elif len(title) > 120:
                flash("The title must be 120 characters or fewer.", "error")
            elif not image or not image.filename:
                flash("Choose an image to upload.", "error")
            elif not _is_allowed_image(image.filename):
                flash("Choose a JPG, PNG, GIF, or WEBP image.", "error")
            else:
                filename = _save_image(image, app.config["UPLOAD_FOLDER"])
                photo = Photo(
                    filename=filename,
                    title=title,
                    description=request.form.get("description", "").strip(),
                )
                db.session.add(photo)
                db.session.commit()
                flash("Photo added to your gallery.", "success")
                return redirect(url_for("index"))

        return render_template("photo_form.html", photo=None, page_title="Add a photo")

    @app.route("/photos/<int:photo_id>/edit", methods=["GET", "POST"])
    def edit_photo(photo_id: int):
        photo = db.get_or_404(Photo, photo_id)

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            image = request.files.get("image")
            has_replacement = bool(image and image.filename)

            if not title:
                flash("Enter a title for the photo.", "error")
            elif len(title) > 120:
                flash("The title must be 120 characters or fewer.", "error")
            elif has_replacement and not _is_allowed_image(image.filename):
                flash("Choose a JPG, PNG, GIF, or WEBP image.", "error")
            else:
                old_filename = photo.filename
                photo.title = title
                photo.description = description
                if has_replacement:
                    photo.filename = _save_image(image, app.config["UPLOAD_FOLDER"])

                db.session.commit()
                if has_replacement:
                    _remove_image(old_filename, app.config["UPLOAD_FOLDER"])
                flash("Photo updated.", "success")
                return redirect(url_for("index"))

        return render_template("photo_form.html", photo=photo, page_title="Edit photo")

    @app.post("/photos/<int:photo_id>/delete")
    def delete_photo(photo_id: int):
        photo = db.get_or_404(Photo, photo_id)
        filename = photo.filename
        db.session.delete(photo)
        db.session.commit()
        _remove_image(filename, app.config["UPLOAD_FOLDER"])
        flash("Photo deleted.", "success")
        return redirect(url_for("index"))

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.cli.command("init-db")
    def init_db() -> None:
        """Create the photo gallery database table."""
        require_postgres_database(app)
        with app.app_context():
            db.create_all()
        print("Photo gallery database is ready.")

    @app.errorhandler(413)
    def upload_too_large(_error):
        flash("Images must be 16 MB or smaller.", "error")
        return redirect(request.referrer or url_for("create_photo"))

    return app


def _is_allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_image(image, upload_folder: str) -> str:
    extension = image.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid4().hex}.{extension}"
    image.save(Path(upload_folder) / filename)
    return filename


def _remove_image(filename: str, upload_folder: str) -> None:
    image_path = Path(upload_folder) / filename
    if image_path.exists():
        image_path.unlink()


def require_postgres_database(app: Flask) -> None:
    database_url = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not isinstance(database_url, str) or not database_url.strip():
        raise RuntimeError(
            "Set DATABASE_URL to a PostgreSQL connection URL before starting this app."
        )
    try:
        parsed_url = make_url(database_url)
    except ArgumentError as error:
        raise RuntimeError(
            "DATABASE_URL must be a valid PostgreSQL connection URL."
        ) from error
    if parsed_url.get_backend_name() != "postgresql":
        raise RuntimeError("DATABASE_URL must use a PostgreSQL connection URL.")
    if not parsed_url.database:
        raise RuntimeError("DATABASE_URL must include a PostgreSQL database name.")


app = create_app()


if __name__ == "__main__":
    require_postgres_database(app)
    app.run(
        debug=True,
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "5000")),
    )
