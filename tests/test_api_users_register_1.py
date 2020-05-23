import os
import sys
import pytest
import sqlite3
import flask
import json
from uuid import uuid4

topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

from flask_back_1 import create_app, db


# pytest -s -o log_cli=true -o log_level=INFO
# t_config = 'test'


def flask_app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "TEST_FLASK_BACK_1_DATABASE_URI"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    )
    # db.init_app(app)
    # @app.teardown_appcontext
    # def delete_tables(exception=None):
    #     db.drop_all()
    return app


@pytest.fixture()
def client():
    app = flask_app()
    with app.test_client() as client:
        db.init_app(app)

        with app.app_context():
            db.create_all()
        yield client

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            db.session.remove()
            db.drop_all()


def test_home_page(client):
    response = client.get("/")
    assert b"HOME" in response.data


def test_get_users(client):
    response = client.get("/api/users")
    response = json.loads(response.data)
    print(response)
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
    # unique_username = str(uuid4())
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
    # unique_username = str(uuid4())
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
