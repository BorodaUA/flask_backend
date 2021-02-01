import os
import sys
import pytest
import json
import logging
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError
from faker import Faker
import random
sys.path.append(os.getcwd())
from flask_backend import create_app # noqa
from api.models import user # noqa

# pytest -s -o log_cli=true -o log_level=DEBUG


@pytest.fixture(scope='function')
def client(request):
    app = create_app(config_name="testing")
    app.config['test_data'] = generate_test_data()
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


def generate_test_data():
    '''
    return Faker's test data user
    '''
    fake = Faker()
    fake_user = fake.profile()
    fake_user['password'] = fake.password(
        length=random.randrange(6, 32)
    )
    return fake_user


def test_signin_user_no_fields(client):
    """
    Test /api/users/signin endpoint with no required fields
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps({}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "username": ["Missing data for required field."],
        "email_address": ["Missing data for required field."],
        "password": ["Missing data for required field."],
    } == response


def test_signin_user_only_username_field(client):
    """
    Test /api/users/signin endpoint with only username field present
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps({"username": "bob_2"}),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "password": ["Missing data for required field."],
        "email_address": ["Missing data for required field."],
    } == response


def test_signin_user_username_and_password_fields(client):
    """
    Test /api/users/signin endpoint with username
    and password fields present
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123456"
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "email_address": ["Missing data for required field."]
    } == response


def test_signin_all_fields_empty(client):
    """
    Test /api/users/signin endpoint with all fields present
    but all of them empty
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "",
                "password": "",
                "email_address": ""
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "username": [
                "Length must be between 3 and 256.",
                "String does not match expected pattern."
            ],
            "password": [
                "Length must be between 6 and 32.",
            ],
            "email_address": [
                "Length must be between 3 and 256."
            ],
        }
    ) == response


def test_signin_user_username_valid_other_fields_empty(client):
    """
    Test /api/users/signin endpoint with valid username field
    other fields empty
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "",
                "email_address": ""
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "password": [
                "Length must be between 6 and 32.",
            ],
            "email_address": [
                "Length must be between 3 and 256."
            ],
        }
    ) == response


def test_signin_valid_username_valid_email_other_fields_empty(client):
    """
    Test /api/users/signin endpoint with valid username,
    email_address fields, password field are empty.
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2",
                "email_address": "bob_2@gmail.com",
                "password": "",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "password": [
                "Length must be between 6 and 32.",
            ],
        }
    ) == response


def test_signin_user_username_too_long(client):
    """
    Test /api/users/signin endpoint with username field
    contain very long string. other fields are valid.
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2" * 150,
                "email_address": "bob_2@gmail.com",
                "password": "123456",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "username": [
                "Length must be between 3 and 256.",
            ],
        }
    ) == response


def test_signin_user_username_email_addres_too_long(client):
    """
    Test /api/users/signin endpoint with username and email
    fields contains very long string. other field is valid.
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2" * 150,
                "email_address": "bob_2@gmail.com" * 150,
                "password": "123456",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "username": [
                "Length must be between 3 and 256.",
            ],
            "email_address": [
                "Length must be between 3 and 256."
            ],
        }
    ) == response


def test_signin_user_username_email_addres_password_too_long(client):
    """
    Test /api/users/signin endpoint with all fields
    contains very long string.
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2" * 150,
                "email_address": "bob_2@gmail.com" * 150,
                "password": "123456" * 150,
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "username": [
                "Length must be between 3 and 256.",
            ],
            "email_address": [
                "Length must be between 3 and 256."
            ],
            "password": [
                "Length must be between 6 and 32.",
            ],
        }
    ) == response
