import os
import sys
import pytest
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import ProgrammingError, OperationalError
sys.path.append(os.getcwd())
from flask_backend import create_app, db # noqa
from api.models import user # noqa

# pytest -s -o log_cli=true -o log_level=DEBUG


@pytest.fixture(scope='function')
def client(request):
    app = create_app("testing")
    db.init_app(app)
    with app.test_client() as client:
        with app.app_context():
            logging.debug('Starting the test.')
            db_name = db.get_engine(bind="flask_backend").url.database
            create_db(test_db_name=db_name)
            test_db_engine = db.get_engine(bind="flask_backend")
            user.Base.session = scoped_session(
                sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=test_db_engine,
                )
            )
            user.Base.query = user.Base.session.query_property()
            user.Base.metadata.create_all(test_db_engine)

        yield client

        @app.teardown_appcontext
        def shutdown_session_and_delete_db(exception=None):
            logging.debug('Shutting down the test.')
            user.Base.session.close()
            test_db_engine.dispose()
            delete_db(test_db_name=db_name)


def create_db(test_db_name):
    default_postgres_db_url = os.environ.get("POSTGRES_DATABASE_URI")
    default_engine = create_engine(default_postgres_db_url)
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


def delete_db(test_db_name):
    default_postgres_db_url = os.environ.get("POSTGRES_DATABASE_URI")
    default_engine = create_engine(default_postgres_db_url)
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

# # pytest -s -o log_cli=true -o log_level=INFO


def test_signin_user_special_symbols_in_username(client):
    """
    Test /api/users/signin endpoint with username field
    contains special characters. other fields are valid.
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2!@#",
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
                "String does not match expected pattern."
            ],
        }
    ) == response


def test_signin_user_special_symbols_in_username_email_addres(client):
    """
    Test /api/users/signin endpoint with username and
    emaild fields contains special characters. other field is valid.
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2!@#",
                "email_address": "bob!_2@gmail.com!@#",
                "password": "123456",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "username": [
                "String does not match expected pattern."
            ],
        }
    ) == response


def test_signin_user_special_symbols_in_username_email_addres_password(client):
    """
    Test /api/users/signin endpoint with all fields
    contains special characters.
    """
    request = client.post(
        "/api/users/signin",
        data=json.dumps(
            {
                "username": "bob_2!@#",
                "email_address": "bob!_2@gmail.com!@#",
                "password": "1234%56!@#",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert (
        {
            "username": [
                "String does not match expected pattern."
            ],
            "password": [
                "String does not match expected pattern.",
            ],
        }
    ) == response


def test_signin_user_invalid_all_credentials(client):
    """
    Test /api/users/signin endpoint with all invalid
    credentials.
    """
    request = client.post(
        "/api/users/register",
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
        "/api/users/register",
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
        "/api/users/register",
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
        "/api/users/register",
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
        "/api/users/register",
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
    request = client.post(
        "/api/users/register",
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
                "email_address": "bob_2@gmail.com",
            }
        ),
        content_type="application/json",
    )
    response = json.loads(request.data)
    assert "Login succesfull bob_2" == response['message']
