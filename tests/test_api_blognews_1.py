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
from api.models import blog_news # noqa

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
            blog_news.Base.metadata.create_all(engine)

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


def test_api_home_page(client):
    """
    Test /api/ endpont
    """
    response = client.get("/api/")
    response = json.loads(response.data)
    assert "Api Home page" == response["message"]


def test_blognews_get_no_pagenumber(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with no pagenumber data
    """
    response = client.get("/api/blognews/",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Field may not be null."]} == response


def test_blognews_get_pagenumber_not_integer(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber not an integer
    """
    response = client.get("/api/blognews/?pagenumber=A",)
    response = json.loads(response.data)
    assert {"pagenumber": ["Not a valid integer."]} == response


def test_blognews_get_pagenumber_is_zero(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber equal to 0
    """
    response = client.get("/api/blognews/?pagenumber=0",)
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_blognews_get_pagenumber_is_negative_number(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber is a negative number
    """
    response = client.get("/api/blognews/?pagenumber=-1",)
    response = json.loads(response.data)
    assert (
        {
            "code": 400,
            "message": "pagenumber must be greater then 0"
        }
    ) == response


def test_blognews_get_pagenumber_is_big_number(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber is a big number, more then pages
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.get("/api/blognews/?pagenumber=100",)
    response = json.loads(response.data)
    assert (
        {
            "code": 404,
            "message": "Pagination page not found"
        }
    ) == response


def test_blognews_get_pagenumber_valid_1(client):
    """
    test GET /api/blognews/?pagenumber=N endpoint
    with pagenumber valid number 1
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response
    response = client.get("/api/blognews/?pagenumber=1",)
    response = json.loads(response.data)
    assert test_user_data['username'] == response['items'][0]['by']


def test_blognews_post_no_json_data(client):
    """
    test POST /api/blognews/ endpoint
    with no json data
    """
    response = client.post(
        "/api/blognews/",
    )
    response = json.loads(response.data)
    assert (
        {
            '_schema': ['Invalid input type.'],

        }
    ) == response


def test_blognews_post_no_required_fields(client):
    """
    test POST /api/blognews/ endpoint
    with no required fields
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps({}),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'url': ['Missing data for required field.'],
            'by': ['Missing data for required field.'],
            'text': ['Missing data for required field.'],
            'title': ['Missing data for required field.'],
        }
    ) == response


def test_blognews_post_empty_required_fields(client):
    """
    test POST /api/blognews/ endpoint
    with empty required fields
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': '',
                'by': '',
                'text': '',
                'title': '',
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'url': ['Shorter than minimum length 1.'],
            'by': ['Shorter than minimum length 2.'],
            'text': ['Shorter than minimum length 1.'],
            'title': ['Shorter than minimum length 1.'],
        }
    ) == response


def test_blognews_post_valid_required_fields(client):
    """
    test POST /api/blognews/ endpoint
    with valid required fields
    """
    test_user_data = client.application.config['test_data']
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': test_user_data['website'][0],
                'by': test_user_data['username'],
                'text': test_user_data['residence'],
                'title': test_user_data['address'],
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'code': 201,
            'message': 'Story added'
        }
    ) == response


def test_blognews_post_invalid_required_fields_types(client):
    """
    test POST /api/blognews/ endpoint
    with invalid required fields types
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': [111],
                'by': 222,
                'text': {'text from test': 333},
                'title': 4.4,
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'url': ['Not a valid string.'],
            'by': ['Not a valid string.'],
            'text': ['Not a valid string.'],
            'title': ['Not a valid string.'],
        }
    ) == response


def test_blognews_post_extra_field(client):
    """
    test POST /api/blognews/ endpoint
    with extra field in the request
    """
    response = client.post(
        "/api/blognews/",
        data=json.dumps(
            {
                'url': 'https://www.google.com/',
                'by': 'test_bob_2',
                'text': 'text from test',
                'title': 'title from test',
                'new_field': 'new field outside the schema'
            }
        ),
        content_type="application/json",
    )
    response = json.loads(response.data)
    assert (
        {
            'new_field': ['Unknown field.']
        }
    ) == response
