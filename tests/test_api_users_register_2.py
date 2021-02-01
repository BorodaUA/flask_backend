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


def test_register_username_too_long_other_fields_valid(client):
    """
    Test /api/users/register endpont
    with 150 characters long "username" field, other fileds valid
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "a" * 150,
                "password": "123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "username": ["Length must be between 2 and 32."],
    } == response


def test_register_username_and_password_too_long_other_fields_valid(client):
    """
    Test /api/users/register endpont
    with 150 characters long "username" and "password" fields
    other fields are valid
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "a" * 150,
                "password": "1" * 150,
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "username": ["Length must be between 2 and 32."],
        "password": ["Length must be between 6 and 32."],
    } == response


def test_register_all_fields_too_long(client):
    """
    Test /api/users/register endpont
    with empty "username" field, other fileds valid
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "a" * 150,
                "password": "a" * 150,
                "email_address": "a@" * 150,
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "username": ["Length must be between 2 and 32."],
        "password": ["Length must be between 6 and 32."],
        "email_address": [
            "Not a valid email address.",
            "Length must be between 3 and 256."
        ],
    } == response


def test_register_no_at_symbol_in_email_field(client):
    """
    Test /api/users/register endpont
    "email_address" field without @ symbol
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123456",
                "email_address": "bob_2gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "email_address": ["Not a valid email address."]
    } == response


def test_register_special_symbols_in_username(client):
    """
    Test /api/users/register endpont
    "email_address" field without @ symbol
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "bob_2!@#$%^&*()",
                "password": "123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert {
        "username": ["String does not match expected pattern."]
    } == response


def test_register_username_valid_password_valid_email_valid(client):
    """
    Test /api/users/register endpont
    with valid "email_address", "username", "password" fields
    """
    test_user_data = client.application.config['test_data']
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": test_user_data['username'],
                "password": test_user_data['password'],
                "email_address": test_user_data['mail'],
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        f"Registration succesfull {test_user_data['username']}"
        == response["message"]
    )


def test_register_duplicate_username_valid_password_valid(client):
    """
    Test /api/users/register endpont
    with valid "email_address", "username", "password" fields 2 times
    with duplicate user credentials
    """
    test_user_data = client.application.config['test_data']
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": test_user_data['username'],
                "password": test_user_data['password'],
                "email_address": test_user_data['mail'],
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        f"Registration succesfull {test_user_data['username']}"
        == response["message"]
    )
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": test_user_data['username'],
                "password": test_user_data['password'],
                "email_address": test_user_data['mail'],
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "User with this username already exist" == response["message"]
