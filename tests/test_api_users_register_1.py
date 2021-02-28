import os
import sys
import pytest
import json
import logging
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError
sys.path.append(os.getcwd())
from flask_backend import create_app # noqa
from api.models import user # noqa

# pytest -s -o log_cli=true -o log_level=DEBUG


@pytest.fixture(scope='function')
def client(request):
    app = create_app(config_name="testing")
    with app.test_client() as client:
        logging.debug('Starting the test.')
        default_postgres_db_uri = app.config['POSTGRES_DATABASE_URI']
        test_db_name = list(
            app.config['SQLALCHEMY_BINDS'].values()
        )[0].split('/')[-1]
        create_db(
            default_postgres_db_uri=default_postgres_db_uri,
            test_db_name=test_db_name,
        )

        @app.before_request
        def create_tables():
            engine = g.flask_backend_session.get_bind()
            user.Base.metadata.create_all(engine)

        yield client

        @app.teardown_appcontext
        def shutdown_session_and_delete_db(exception=None):
            logging.debug('Shutting down the test.')
            if g.flask_backend_session:
                g.flask_backend_session.remove()
                engine = g.flask_backend_session.get_bind()
                engine.dispose()
            if g.hacker_news_session:
                g.hacker_news_session.remove()
                engine = g.hacker_news_session.get_bind()
                engine.dispose()
            delete_db(
                default_postgres_db_uri=default_postgres_db_uri,
                test_db_name=test_db_name,
            )


def create_db(default_postgres_db_uri, test_db_name):
    default_engine = create_engine(default_postgres_db_uri)
    default_engine = default_engine.execution_options(
        isolation_level="AUTOCOMMIT"
    )
    conn = default_engine.connect()
    # Try to delete Database
    try:
        conn.execute(
            f"DROP DATABASE "
            f"{test_db_name};"
        )
    except ProgrammingError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    except OperationalError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    # Try to create Database
    try:
        conn.execute(
            f"CREATE DATABASE "
            f"{test_db_name} "
            f"ENCODING 'utf8' TEMPLATE template1"
        )
    except ProgrammingError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    except OperationalError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    conn.close()
    default_engine.dispose()
    return


def delete_db(default_postgres_db_uri, test_db_name):
    default_engine = create_engine(default_postgres_db_uri)
    default_engine = default_engine.execution_options(
        isolation_level="AUTOCOMMIT"
    )
    conn = default_engine.connect()
    try:
        conn.execute(
            f"DROP DATABASE "
            f"{test_db_name};"
        )
    except ProgrammingError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    except OperationalError as err:
        logging.debug(err)
        conn.execute("ROLLBACK")
    conn.close()
    default_engine.dispose()
    return


def test_api_home_page(client):
    """
    Test /api/ endpont
    """
    response = client.get("/api/")
    response = json.loads(response.data)
    assert "Api Home page" == response["message"]


def test_get_users(client):
    """
    Test /api/users endpont
    """
    response = client.get("/api/users")
    response = json.loads(response.data)
    assert {"code": 404, "message": "users not found"} == response


def test_register_user_no_fields(client):
    """
    Test /api/users/register endpont
    with no required fields "email_address", "username", "password"
    """
    request = client.post(
        "/api/users",
        data=json.dumps({}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "email_address": ["Missing data for required field."],
        "username": ["Missing data for required field."],
        "password": ["Missing data for required field."],
    } == response


def test_register_user_username_valid(client):
    """
    Test /api/users/register endpont
    with no required fields "email_address", "password"
    """
    request = client.post(
        "/api/users",
        data=json.dumps({"username": "bob_2"}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "email_address": ["Missing data for required field."],
        "password": ["Missing data for required field."],
    } == response


def test_register_user_username_valid_password_valid(client):
    """
    Test /api/users/register endpont with no required fields
    "email_address"
    """
    request = client.post(
        "/api/users",
        data=json.dumps({"username": "bob_2", "password": "123456"}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "email_address": ["Missing data for required field."]
    } == response


def test_register_username_empty_other_fields_valid(client):
    """
    Test /api/users/register endpont
    with empty "username" field, other fileds valid
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "",
                "password": "123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "username": [
            "Length must be between 2 and 32.",
            "String does not match expected pattern."
        ]
    } == response


def test_register_username_empty_password_empty_other_fields_valid(client):
    """
    Test /api/users/register endpont
    with empty "username" field, other fileds valid
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "",
                "password": "",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "username": [
            "Length must be between 2 and 32.",
            "String does not match expected pattern."
        ],
        "password": [
            "Length must be between 6 and 32."
        ],
    } == response


def test_register_all_fields_empty(client):
    """
    Test /api/users/register endpont
    with empty "username" field, other fileds valid
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "",
                "password": "",
                "email_address": "",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "username": [
            "Length must be between 2 and 32.",
            "String does not match expected pattern."
        ],
        "password": [
            "Length must be between 6 and 32.",
        ],
        "email_address": [
            "Not a valid email address.",
            "Length must be between 3 and 256."
        ],
    } == response
