from io import BytesIO

import pytest

from app import Photo, create_app, db


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'gallery.sqlite'}",
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )
    with app.app_context():
        db.create_all()
    with app.test_client() as test_client:
        yield test_client
    with app.app_context():
        db.session.remove()
        db.drop_all()


def _csrf_token(client):
    response = client.get("/photos/new")
    return response.text.split('name="csrf_token" value="')[1].split('"')[0]


def test_gallery_shows_empty_state(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Your gallery starts here" in response.data


def test_add_photo(client, tmp_path):
    response = client.post(
        "/photos/new",
        data={
            "csrf_token": _csrf_token(client),
            "title": "Mountain morning",
            "description": "A quiet start",
            "image": (BytesIO(b"sample photo"), "mountain.jpg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Mountain morning" in response.data
    with client.application.app_context():
        photo = db.session.scalar(db.select(Photo))
        assert photo.title == "Mountain morning"
        assert (tmp_path / "uploads" / photo.filename).read_bytes() == b"sample photo"


def test_edit_photo_and_replace_image(client, tmp_path):
    token = _csrf_token(client)
    client.post(
        "/photos/new",
        data={
            "csrf_token": token,
            "title": "Before",
            "description": "",
            "image": (BytesIO(b"old image"), "before.jpg"),
        },
        content_type="multipart/form-data",
    )
    with client.application.app_context():
        photo = db.session.scalar(db.select(Photo))
        photo_id, old_filename = photo.id, photo.filename

    response = client.post(
        f"/photos/{photo_id}/edit",
        data={
            "csrf_token": token,
            "title": "After",
            "description": "Updated caption",
            "image": (BytesIO(b"new image"), "after.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"After" in response.data
    assert b"Updated caption" in response.data
    assert not (tmp_path / "uploads" / old_filename).exists()
    with client.application.app_context():
        photo = db.session.get(Photo, photo_id)
        assert (tmp_path / "uploads" / photo.filename).read_bytes() == b"new image"


def test_reject_non_image_file(client):
    response = client.post(
        "/photos/new",
        data={
            "csrf_token": _csrf_token(client),
            "title": "A document",
            "image": (BytesIO(b"not an image"), "notes.txt"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Choose a JPG, PNG, GIF, or WEBP image." in response.data
    with client.application.app_context():
        assert db.session.scalar(db.select(Photo)) is None


def test_delete_photo_removes_record_and_uploaded_file(client, tmp_path):
    token = _csrf_token(client)
    client.post(
        "/photos/new",
        data={
            "csrf_token": token,
            "title": "Remove me",
            "image": (BytesIO(b"photo data"), "remove.jpg"),
        },
        content_type="multipart/form-data",
    )
    with client.application.app_context():
        photo = db.session.scalar(db.select(Photo))
        photo_id, filename = photo.id, photo.filename

    response = client.post(
        f"/photos/{photo_id}/delete",
        data={"csrf_token": token},
    )

    assert response.status_code == 302
    with client.application.app_context():
        assert db.session.get(Photo, photo_id) is None
    assert not (tmp_path / "uploads" / filename).exists()


def test_write_requires_csrf_token(client):
    response = client.post("/photos/1/delete")

    assert response.status_code == 400
