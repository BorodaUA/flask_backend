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


@pytest.fixture()
def client():
    app = create_app("testing")
    with app.test_client() as client:
        db.init_app(app)

        with app.app_context():
            db.create_all()

        yield client

        @app.teardown_appcontext
        def shutdown_session_and_delete_table(exception=None):
            db.session.remove()
            db.drop_all()


def test_signin_user_no_fields(client):
    request = client.get("/api/users")
    print(request.data)
    request = client.post(
        "/api/users/signin", data=json.dumps({}), content_type="application/json",
    )
    response = json.loads(request.data)
    # print(response)
    assert {
        "email_address": ["Missing data for required field."],
        "username": ["Missing data for required field."],
        "password": ["Missing data for required field."],
    } == response


def test_signin_user_no_fields_but_username(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps({"username": "bob_2"}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    # print(response)
    assert {
        "email_address": ["Missing data for required field."],
        "password": ["Missing data for required field."],
    } == response


def test_signin_user_no_fields_but_username_and_password(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps({"username": "bob_2", "password": "123"}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    # print(response)
    assert {"email_address": ["Missing data for required field."]} == response


def test_signin_all_fields_empty(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps({"username": "", "password": "", "email_address": ""}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "username": ["Length must be between 3 and 128."],
            "password": ["Length must be between 3 and 128."],
            "email_address": ["Length must be between 3 and 128."],
        }
    ) == response


def test_signin_invalid_username_other_fields_empty(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps({"username": "not_a_bob", "password": "", "email_address": ""}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "password": ["Length must be between 3 and 128."],
            "email_address": ["Length must be between 3 and 128."],
        }
    ) == response


def test_signin_invalid_username_invalid_email_other_fields_empty(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "not_a_bob",
                "password": "",
                "email_address": "not_bob@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert ({"password": ["Length must be between 3 and 128."],}) == response


def test_signin_invalid_username_invalid_email_invalid_password(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "not_a_bob",
                "password": "not_valid_password",
                "email_address": "not_bob@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    # print(response)
    assert {"message": "Username or Email address not found."} == response


def test_signin_valid_username_invalid_email_invalid_password(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob",
                "password": "not_valid_password",
                "email_address": "not_bob@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    # print(response)
    assert {"message": "Username or Email address not found."} == response


def test_signin_valid_username_valid_email_invalid_password(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob",
                "password": "not_valid_password",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    # print(response)
    assert {"message": "Username or Email address not found."} == response


def test_signin_invalid_username_valid_email_invalid_password(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "not_bob",
                "password": "not_valid_password",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {"message": "Username or Email address not found."} == response


def test_signin_invalid_username_valid_email_valid_password(client):
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
    ###
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "not_bob",
                "password": "123",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Login succesfull bob_2@gmail.com" == response["message"]


def test_signin_valid_username_invalid_email_valid_password(client):
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
    assert "Registration succesfull bob_2" in response["message"]
    ###
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123",
                "email_address": "not_bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Login succesfull bob_2" == response["message"]


def test_signin_very_long_username_invalid_email_valid_password(client):
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2not_bob_2",
                "password": "123",
                "email_address": "not_bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    # print(response)
    assert {"username": ["Length must be between 3 and 128."]} == response
