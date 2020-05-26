import os
import sys
import pytest
import flask
import json
from uuid import uuid4

topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

from flask_back_1 import create_app, db
from api.models import user
from sqlalchemy.orm import scoped_session, sessionmaker


# pytest -s -o log_cli=true -o log_level=INFO


@pytest.fixture()
def client():
    app = create_app("testing")
    with app.test_client() as client:
        db.init_app(app)

        with app.app_context():
            user.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=db.get_engine(bind="flask_back_1"),
                )
            )
            user.Base.query = user.Base.session.query_property()
            user.Base.metadata.create_all(db.get_engine(bind="flask_back_1"))

        yield client

        @app.teardown_appcontext
        def shutdown_session_and_delete_table(exception=None):
            user.Base.session.remove()
            user.Base.metadata.drop_all(db.get_engine(bind="flask_back_1"))


def test_api_home_page(client):
    response = client.get("/api/")
    response = json.loads(response.data)
    assert "Api Home page" == response["message"]


def test_get_users(client):
    response = client.get("/api/users")
    response = json.loads(response.data)
    assert "message" in response


def test_add_user_no_fields(client):
    request = client.post(
        "/api/users/register", data=json.dumps({}), content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "email_address": ["Missing data for required field."],
        "username": ["Missing data for required field."],
        "password": ["Missing data for required field."],
    } == response


def test_add_user_username_valid(client):
    request = client.post(
        "/api/users/register",
        data=json.dumps({"username": "bob_2"}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "email_address": ["Missing data for required field."],
        "password": ["Missing data for required field."],
    } == response


def test_add_user_username_valid_password_valid(client):
    request = client.post(
        "/api/users/register",
        data=json.dumps({"username": "bob_2", "password": "123"}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {"email_address": ["Missing data for required field."]} == response


def test_add_user_username_valid_password_valid(client):
    request = client.post(
        "/api/users/register",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123",
                "email_address": f"bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert f"Registration succesfull bob_2" in response["message"]


def test_add_duplicate_username_valid_password_valid(client):
    request = client.post(
        "/api/users/register",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123",
                "email_address": f"bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert f"Registration succesfull bob_2" in response["message"]
    request = client.post(
        "/api/users/register",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123",
                "email_address": f"bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert f"User with this username already exist" in response["message"]
