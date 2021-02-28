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


def test_signin_user_invalid_all_credentials(client):
    """
    Test /api/users/signin endpoint with all invalid
    credentials.
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Registration succesfull bob_2" == response["message"]
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
    assert {"message": "Username or Email address not found."} == response


def test_signin_valid_username_invalid_email_invalid_password(client):
    """
    Test /api/users/signin endpoint with:
    -valid username
    -invalid password
    -invalid email
    credentials.
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Registration succesfull bob_2" == response["message"]
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "not_valid_password",
                "email_address": "not_bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "message": "Username or password Incorect!"
        } == response
    )


def test_signin_invalid_username_invalid_password_valid_email(client):
    """
    Test /api/users/signin endpoint with:
    -invalid username
    -invalid password
    -valid email
    credentials.
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Registration succesfull bob_2" == response["message"]
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "Not_valid_bob_2",
                "password": "wrong123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "message": "Email address or password Incorect!"
        } == response
    )


def test_signin_valid_username_valid_password_invalid_email(client):
    """
    Test /api/users/signin endpoint with:
    -valid username
    -valid password
    -invalid email
    credentials.
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Registration succesfull bob_2" == response["message"]
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123456",
                "email_address": "not_bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Login succesfull bob_2" == response['message']


def test_signin_invalid_username_valid_password_valid_email(client):
    """
    Test /api/users/signin endpoint with:
    -invalid username
    -valid password
    -valid email
    credentials.
    """
    request = client.post(
        "/api/users",
        data=json.dumps(
            {
                "username": "bob_2",
                "password": "123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Registration succesfull bob_2" == response["message"]
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "Not_valid_bob_2",
                "password": "123456",
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Login succesfull bob_2@gmail.com" == response['message']


def test_signin_valid_username_valid_password_valid_email(client):
    """
    Test /api/users/signin endpoint with:
    -valid username
    -valid password
    -valid email
    credentials.
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
        "/api/users/signin",
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
        f"Login succesfull {test_user_data['username']}"
        == response['message']
    )
